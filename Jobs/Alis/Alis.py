from alis_utils import get_network_generator, get_image_from_w_alis, save_img, prepare_img

import os
import copy
import PIL
from PIL import Image
import imageio
import pickle as pkl
import imghdr
from time import perf_counter

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.decomposition import PCA

from alis import dnnlib
from alis.scripts import legacy
from alis.scripts.legacy import load_network_pkl
from alis.training.networks import SynthesisLayer


'''
    Static class to wrap up methods used in endpoints related to Alis network
'''
class AlisWrapper:
    
    '''
    **************************************************************************************************
        Get Random Image Stuff
    **************************************************************************************************
    '''
    
    @classmethod
    def get_random_images(
        cls,
        network_pkl = 'https://kaust-cair.s3.amazonaws.com/alis/lhq1024-snapshot.pkl',
        device = torch.device('cuda'),
        n_samples = 1,
    ):
        '''
            Method to get random images from alis network.
            Args:
                network_pkl (str): Where to get the checkpoint, is by default set up to alis cloud checkpoint
                device (str | torch.device): Is set to use cuda device (not sure cpu or other device is suupported by alis repo)
                n_samples (int): Amount of random images to generate
            
            Returns:
                w_list (list): List of latent vectors for generated images
                img_list (list): List of image matrices 
        '''
        c = None
        modes_idx = torch.from_numpy(np.array([0])).to(device)
        
        G = get_network_generator(network_pkl)
        G.eval()
        
        w_list = []
        img_list = []
        for i in range(n_samples):
            z = torch.randn((2, G.z_dim), device=device)    
            w = G.mapping(z, c, modes_idx=modes_idx)
            
            img = get_image_from_w_alis(G, w)
            img = prepare_img(img)

            w_list.append(w.detach())
            img_list.append(img)
        
        return w_list, img_list
    
    
    '''
    **************************************************************************************************
        Projection stuff
    **************************************************************************************************
    '''
    
    @classmethod
    def get_image_from_w(cls, G, ws, device=torch.device('cuda')):
        '''
            Method to get image from ws context in projection process
            Args:
                G (GeneratorNetwork): alis generator.
                ws (torch.tensor): tensor with shape (3, G.w_dim)
                device (str|torch.device): is set to use cuda device (not sure cpu or other device is suupported by alis repo)
            Returns:
                synth_images (list): The list of image matrices
        '''
        curr_idx = 1
        curr_ws = ws[curr_idx].unsqueeze(0)
        left_ws = ws[curr_idx - 1].unsqueeze(0)
        right_ws = ws[curr_idx + 1].unsqueeze(0)
        curr_ws_context = torch.stack([left_ws, right_ws], dim=1)
        left_borders_idx=torch.tensor([0], requires_grad=False).to(device)

        synth_images = G.synthesis(curr_ws, ws_context=curr_ws_context, left_borders_idx=left_borders_idx, noise_mode='const')
        return synth_images


    @classmethod
    def project( 
        cls,
		G,
		target: torch.Tensor, # [C,H,W] and dynamic range [0,255], W & H must match G output resolution
		*,
		num_steps                  = 2000,
		w_avg_samples              = 10000,
		initial_learning_rate      = 0.1,
		initial_noise_factor       = 0.05,
		lr_rampdown_length         = 0.25,
		lr_rampup_length           = 0.05,
		noise_ramp_length          = 0.75,
		regularize_noise_weight    = 1e5,
		verbose                    = False,
		device: torch.device	   = torch.device('cuda')
    ):
        '''
            Method to project an image to latent space.
            Args:
                G: alis generator.
                target: target image to project
                num_steps: amount of iteration of optimization process
                w_avg_samples: amount of samples to average for starting point of optimization
                [initial_learning_rate, initial_noise_factor, lr_rampdown_length, lr_rampup_length,
                    noise_ramp_length, regularize_noise_weight]: optimization hyperparameters
                verbose: whether to print stuff from optimization process
                device: is set to use cuda device (not sure cpu or other device is suupported by alis repo)
            Returns:
                z_out (list): List of latent vectors in Z space for each optimization step
        '''
        assert target.shape == (G.img_channels, G.img_resolution, G.img_resolution)

        def logprint(*args):
            if verbose:
                print(*args)

        G = copy.deepcopy(G).eval().requires_grad_(False).to(device) # type: ignore
        modes_idx = torch.tensor([0], device=device)

        # Compute w stats.
        logprint(f'Computing W midpoint and stddev using {w_avg_samples} samples...')
        z_samples = np.random.RandomState(123).randn(w_avg_samples, G.z_dim)
        w_samples = G.mapping(torch.from_numpy(z_samples).to(device), None, modes_idx=modes_idx)  # [N, L, C]
        
        w_samples = w_samples[:, :1, :].cpu().numpy().astype(np.float32)       # [N, 1, C]

        w_avg = np.mean(w_samples, axis=0, keepdims=True)      # [1, 1, C]
        w_std = (np.sum((w_samples - w_avg) ** 2) / w_avg_samples) ** 0.5

        # Setup noise inputs.
        noise_bufs = { name: buf for (name, buf) in G.synthesis.named_buffers() if 'noise_const' in name }

        # Load VGG16 feature detector.
        url = 'https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/metrics/vgg16.pt'
        with dnnlib.util.open_url(url) as f:
            vgg16 = torch.jit.load(f).eval().to(device)

        # Features for target image.
        target_images = target.unsqueeze(0).to(device).to(torch.float32)
        if target_images.shape[2] > 256:
            target_images = F.interpolate(target_images, size=(256, 256), mode='area')
        target_features = vgg16(target_images, resize_images=False, return_lpips=True)

        # Init noise.
        for buf in noise_bufs.values():
            buf[:] = torch.randn_like(buf)
            buf.requires_grad_(True)    

        z_opt = torch.tensor(z_samples[:3], dtype=torch.float32, device=device, requires_grad=True) # pylint: disable=not-callable
        z_out = []
        optimizer = torch.optim.Adam([z_opt] + list(noise_bufs.values()), betas=(0.9, 0.999), lr=initial_learning_rate)

        for step in range(num_steps):
            # Learning rate schedule.
            t = step / num_steps
            w_noise_scale = w_std * initial_noise_factor * max(0.0, 1.0 - t / noise_ramp_length) ** 2
            lr_ramp = min(1.0, (1.0 - t) / lr_rampdown_length)
            lr_ramp = 0.5 - 0.5 * np.cos(lr_ramp * np.pi)
            lr_ramp = lr_ramp * min(1.0, t / lr_rampup_length)
            lr = initial_learning_rate * lr_ramp
            for param_group in optimizer.param_groups:
                param_group['lr'] = lr

            ws = G.mapping(z_opt, c=None, modes_idx=modes_idx)
            ws.requires_grad_(True)

            w_noise = torch.randn((19, 512), dtype=torch.float).to(device) * w_noise_scale
            w_noise.requires_grad_(True)

            ws = (ws + w_noise)
        
            curr_idx = 1
            curr_ws = ws[curr_idx].unsqueeze(0)
            left_ws = ws[curr_idx - 1].unsqueeze(0)
            right_ws = ws[curr_idx + 1].unsqueeze(0)
            curr_ws_context = torch.stack([left_ws, right_ws], dim=1)
            left_borders_idx=torch.tensor([0], requires_grad=False).to(device)

            synth_images = G.synthesis(curr_ws, ws_context=curr_ws_context, left_borders_idx=left_borders_idx, noise_mode='const')
            synth_images.requires_grad_(True)

            synth_images = (synth_images + 1) * (255/2)
            if synth_images.shape[2] > 256:
                synth_images = F.interpolate(synth_images, size=(256, 256), mode='area')

            # Features for synth images.
            synth_features = vgg16(synth_images, resize_images=False, return_lpips=True)
            dist = (target_features - synth_features).square().sum()

            # Noise regularization.
            reg_loss = 0.0
            for v in noise_bufs.values():
                noise = v[None,None,:,:] # must be [1,1,H,W] for F.avg_pool2d()
                while True:
                    reg_loss += (noise*torch.roll(noise, shifts=1, dims=3)).mean()**2
                    reg_loss += (noise*torch.roll(noise, shifts=1, dims=2)).mean()**2
                    if noise.shape[2] <= 8:
                        break
                    noise = F.avg_pool2d(noise, kernel_size=2)

            loss = dist + reg_loss * regularize_noise_weight
            loss.requires_grad_(True)

            # Step
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()#%%
            logprint(f'step {step+1:>4d}/{num_steps}: dist {dist:<4.2f} loss {float(loss):<5.2f}')

            # Save projected W for each optimization step.
            z_out.append(z_opt.detach().clone())

        return z_out
    
    
    @classmethod
    def run_project(
        cls, 
		network_pkl: str,
		target_fname: str, 
		outdir: str, 
		out_name: str,
		save_video: bool = True, 
		seed: int = 303, 
		num_steps: int = 2000,
		verbose: bool = False,
    ):
        '''
            Method to drive projection given file, preprocess target file, load network and saves projection
            Args:
                network_pkl (str): Where to get the checkpoint, is by default set up to alis cloud checkpoint
                target_fname (str): Path to target image file
                outdir (str): Path to target output folder
                out_name (str): Output's file name
                save_video (boolean): Whether to save a video with the optimization process
                seed (int): random seed
                num_steps (int): Amount of Iterations for optimization process
                verbose (boolean): Whether to print stuff from optimization process
            Returns:
                None: This method does not return any value.
        '''
        np.random.seed(seed)
        torch.manual_seed(seed)
        device = torch.device('cuda')
        modes_idx = torch.tensor([0], device=device)

        # Load networks.
        print('Loading networks from "%s"...' % network_pkl)
        with dnnlib.util.open_url(network_pkl) as fp:
            G = legacy.load_network_pkl(fp)['G_ema'].requires_grad_(False).to(device) # type: ignore

        # Load target image.
        target_pil = PIL.Image.open(target_fname).convert('RGB')
        w, h = target_pil.size
        s = min(w, h)
        target_pil = target_pil.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
        target_pil = target_pil.resize((G.img_resolution, G.img_resolution), PIL.Image.LANCZOS)
        target_uint8 = np.array(target_pil, dtype=np.uint8)

        # Optimize projection.
        start_time = perf_counter()
        projected_z_steps = AlisWrapper.project(
            G,
            target=torch.tensor(target_uint8.transpose([2, 0, 1]), device=device), # pylint: disable=not-callable
            num_steps=num_steps,
            device=device,
            verbose=verbose
        )

        print (f'Elapsed: {(perf_counter()-start_time):.1f} s')

        # Render debug output: optional video and projected image and W vector.
        os.makedirs(outdir, exist_ok=True)
        if save_video:
            video_name = os.path.join(outdir, out_name + '.mp4')
            video = imageio.get_writer(f'{video_name}', mode='I', fps=10, codec='libx264', bitrate='16M')
            print (f'Saving optimization progress video "{video_name}"')
            for projected_z in projected_z_steps:
                projected_w = G.mapping(projected_z, c=None, modes_idx=modes_idx)
                synth_image = AlisWrapper.get_image_from_w(G, projected_w)
                synth_image = (synth_image + 1) * (255/2)
                synth_image = synth_image.permute(0, 2, 3, 1).clamp(0, 255).to(torch.uint8)[0].cpu().numpy()
                video.append_data(np.concatenate([target_uint8, synth_image], axis=1))
            video.close()

        # Save final projected frame and W vector.
        projected_z = projected_z_steps[-1]
        projected_w = G.mapping(projected_z, c=None, modes_idx=modes_idx)
        synth_image = AlisWrapper.get_image_from_w(G, projected_w)
        synth_image = (synth_image + 1) * (255/2)
        synth_image = synth_image.permute(0, 2, 3, 1).clamp(0, 255).to(torch.uint8)[0].cpu().numpy()
        
        PIL.Image.fromarray(synth_image, 'RGB').save(os.path.join(outdir, out_name + '.png'))

        # Save W to pickle file
        with open(os.path.join(outdir, out_name + '.pkl'), 'wb') as f:
            pkl.dump(projected_w[:2], f)

    
    @classmethod
    def run_projection_on_file(
        cls,
        file_path : str,
        out_folder : str,
        save_video : bool = False,
        num_steps : int = 2000,
        verbose : bool = False
    ):
        '''
            Exposed method for endpoint to start the projection process on a single image file:
            Args:
                file_path (str): Path to target image file
                out_folder (str): Path to output folder for storing results of projection
                save_video (boolean): Wheter to save a video with the optimization process
                num_steps (int): Amount of iteration of optimization process
                verbose (boolean): Whether to print stuff from optimization process
            Returns:
                None: This method does not return any value.
        '''
        
        # Get the name of the file
        file_name = os.path.basename(file_path)

        print("File name:", file_name)

        # Get the path of the file
        file_dir = os.path.dirname(file_path)
        print("File directory:", file_dir)
        name, ext = file_name.split('.')
        
        if imghdr.what(file_path) is None:
            print(f'File {file_path} is not an image. Skipping it...')
            return

        print('Running projection on ' + file_path)
        AlisWrapper.run_project(
            network_pkl = 'https://kaust-cair.s3.amazonaws.com/alis/lhq1024-snapshot.pkl',
            target_fname = file_path,
            outdir = out_folder,
            save_video = save_video,
            num_steps = num_steps,
            out_name = name,
            verbose = verbose
        )

    
    
    '''
    **************************************************************************************************
        PCA moving stuff
    **************************************************************************************************
    '''
    def move(
        interpolation_steps,    #amount of interpolation samples
        outdir : str, 
        w : torch.tensor        = None, # if w is None its randomly sampled a point on Z space to perform movement 
        device : torch.device   = torch.device('cuda'),
        n_samples : int         = 10000, #number of samples to compute pca
        fit_pca : bool          = True, #whether to compute pca or if it's already calculated
        modify_list : list      = [], #each item is a tuple of the form (principal_component_number, (start_layer, end_layer), (lower_coeff_limit, upper_coeff_limit))
    ):
        '''
            Apply pca moving on given latent vector and desired modifications
            Args:
                interpolation_steps (int): How many samples to generate during moving step?
                outdir (str): Path to output folder
                w (torch.tensor): Latent vector:
                n_samples (int): Number of samples to fit pca
                fit_pca (boolean): Whether to compute PCA or used a previous pkl file with PCA object
                modify_list (list): List with all the modifications to apply
            Returns:
                None: This method does not return any value.
        '''
        c = None
        modes_idx = torch.from_numpy(np.array([0])).to(device)

        G = get_network_generator()
        G.eval()

        pca_path = os.path.join(outdir, '..', 'pca.pkl')

        if fit_pca:
            zs = torch.randn([n_samples, G.z_dim], device=device)
            ws = G.mapping(zs, c=None, skip_w_avg_update=True, modes_idx=modes_idx)[:, 0, :].detach().cpu().numpy()            
            pca = PCA(n_components=G.w_dim).fit(ws)
            with open(pca_path, 'wb') as f:
                pkl.dump(pca, f)
        else:
            with open(pca_path, 'rb') as f:
                pca = pkl.load(f)

        if w is None:
            z = torch.randn([2, G.z_dim], device=device)
            w = G.mapping(z, c=None, skip_w_avg_update=True, modes_idx=modes_idx)#torch.nn.functional.one_hot(torch.tensor([cur_class]), n_classes).to(device))

        ws = w.unsqueeze(0).repeat([interpolation_steps, 1, 1, 1])

        for (comp, (l_layer, r_layer), (l_coeff, r_coeff)) in modify_list:
            v = np.zeros((1, G.w_dim))
            v[0, comp] = 1
            u = pca.inverse_transform(v) - pca.mean_
            n_layers = r_layer - l_layer + 1
            u = torch.tensor(u, device=device)#.unsqueeze(0).repeat([2, n_layers, 1])

            coeff = torch.linspace(l_coeff, r_coeff, interpolation_steps, device=device).reshape(interpolation_steps, 1, 1, 1).repeat([1, 2, n_layers, G.w_dim])
            mov = coeff * u

            ws[:, :, l_layer:r_layer+1, :] += mov

        
        os.makedirs(outdir, exist_ok=True)

        for i in range(interpolation_steps):
            img = get_image_from_w_alis(G, ws[i])
            img = prepare_img(img)
            save_img(img, os.path.join(outdir, f'{i}.jpg'))


    def run_pca_moving_on_file(
        file_path: str,
        out_folder: str,
        interpolation_steps: int,
        latent_edits: list
    ):
        '''
            Driver to run pca moving on an image file
            Args:
                file_path (str): Path to pkl with latent vector
                out_folder (str): Path to output folder
                interpolation_steps (int): How many samples to generate during moving step?
                latent_edits (list): List with all the modifications to apply
            Returns:
                None: This method does not return any value.
        '''
        fit_pca = True

        # Get the name of the file
        file_name = os.path.basename(file_path)

        print("File name:", file_name)

        # Get the path of the file
        file_dir = os.path.dirname(file_path)
        print("File directory:", file_dir)

        name, ext = file_name.split('.')

        if ext != 'pkl':
            print(f'File {file_path} is not a pickle file. Skipping it...')
            return False
        
        with open(file_path, 'rb') as f:
            w = pkl.load(f)
        outdir = os.path.join(out_folder, name)
        os.makedirs(outdir, exist_ok=True)

        AlisWrapper.move(
            interpolation_steps = interpolation_steps,
            outdir = outdir,
            w = w,
            modify_list = latent_edits,
            fit_pca = fit_pca
        )
        
        