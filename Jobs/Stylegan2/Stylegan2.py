import os
import torch
import numpy as np
import pickle as pkl
import PIL
import imghdr
from PIL import Image
import imageio
from time import perf_counter
import torch.nn.functional as F
import copy

from stylegan2 import dnnlib
from stylegan2 import legacy

from stylegan2_utils import get_image_from_w, get_network_generator, prepare_img

class Stylegan2Wrapper:
    @classmethod
    def get_random_images(
        cls,
        network_pkl = 'https://nvlabs-fi-cdn.nvidia.com/stylegan2/networks/stylegan2-church-config-f.pkl',
        device = torch.device('cuda'),
        n_samples = 1,
    ):
        '''
            Method to get random images from stylegan2 network.
            Args:
                network_pkl (str): Where to get the checkpoint, is by default set up to church dataset cloud checkpoint
                device (str | torch.device): Is set to use cuda device (not sure cpu or other device is suupported by stylegan2 repo)
                n_samples (int): Amount of random images to generate
            
            Returns:
                w_list (list): List of latent vectors for generated images
                img_list (list): List of image matrices 
        '''

        G = get_network_generator(network_pkl)        

        zs = torch.randn((n_samples, G.z_dim)).to(device)
        ws = G.mapping(zs, None) 

        w_list = []
        img_list = []
        for i in range(n_samples):
            img = get_image_from_w(G, ws[i:i+1])
            img = prepare_img(img)

            w_list.append(ws[i].detach())
            img_list.append(img)            
        
        return w_list, img_list
    

    @classmethod
    def project(
        cls,
        G,
        target: torch.Tensor, # [C,H,W] and dynamic range [0,255], W & H must match G output resolution
        num_steps                  = 2000,
        w_avg_samples              = 10000,
        initial_learning_rate      = 0.1,
        initial_noise_factor       = 0.05,
        lr_rampdown_length         = 0.25,
        lr_rampup_length           = 0.05,
        noise_ramp_length          = 0.75,
        regularize_noise_weight    = 1e5,
        verbose                    = False,
        device: torch.device       = 'cuda'
    ):
        assert target.shape == (G.img_channels, G.img_resolution, G.img_resolution)

        def logprint(*args):
            if verbose:
                print(*args)

        G = copy.deepcopy(G).eval().requires_grad_(False).to(device) # type: ignore

        # Compute w stats.
        logprint(f'Computing W midpoint and stddev using {w_avg_samples} samples...')
        z_samples = np.random.RandomState(123).randn(w_avg_samples, G.z_dim)
        w_samples = G.mapping(torch.from_numpy(z_samples).to(device), None)  # [N, L, C]
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

        w_opt = torch.tensor(w_avg, dtype=torch.float32, device=device, requires_grad=True) # pylint: disable=not-callable
        w_out = torch.zeros([num_steps] + list(w_opt.shape[1:]), dtype=torch.float32, device=device)
        optimizer = torch.optim.Adam([w_opt] + list(noise_bufs.values()), betas=(0.9, 0.999), lr=initial_learning_rate)

        # Init noise.
        for buf in noise_bufs.values():
            buf[:] = torch.randn_like(buf)
            buf.requires_grad = True

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

            # Synth images from opt_w.
            w_noise = torch.randn_like(w_opt) * w_noise_scale
            ws = (w_opt + w_noise).repeat([1, G.mapping.num_ws, 1])
            synth_images = G.synthesis(ws, noise_mode='const')

            # Downsample image to 256x256 if it's larger than that. VGG was built for 224x224 images.
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

            # Step
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            logprint(f'step {step+1:>4d}/{num_steps}: dist {dist:<4.2f} loss {float(loss):<5.2f}')

            # Save projected W for each optimization step.
            w_out[step] = w_opt.detach()[0]

            # Normalize noise.
            with torch.no_grad():
                for buf in noise_bufs.values():
                    buf -= buf.mean()
                    buf *= buf.square().mean().rsqrt()

        return w_out.repeat([1, G.mapping.num_ws, 1])

    @classmethod
    def run_project(
        cls,
        network_pkl: str,
        target_fname: str,
        outdir: str,
        out_name : str,
        save_video: bool       = False,
        seed: int = 123,
        num_steps : int = 2000,
        device : torch.device = torch.device('cuda'),
        verbose : bool         = False
    ):
        np.random.seed(seed)
        torch.manual_seed(seed)
        G = get_network_generator(network_pkl, device)
        
        # Load target image.
        target_pil = PIL.Image.open(target_fname).convert('RGB')
        w, h = target_pil.size
        s = min(w, h)
        target_pil = target_pil.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
        target_pil = target_pil.resize((G.img_resolution, G.img_resolution), PIL.Image.LANCZOS)
        target_uint8 = np.array(target_pil, dtype=np.uint8)

        # Optimize projection.
        start_time = perf_counter()
        projected_w_steps = Stylegan2Wrapper.project(
            G,
            target=torch.tensor(target_uint8.transpose([2, 0, 1]), device=device), # pylint: disable=not-callable
            num_steps=num_steps,
            device=device,
            verbose=verbose
        )
        print (f'Elapsed: {(perf_counter()-start_time):.1f} s')

        # Save final projed latent
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, out_name + '.pkl'), 'wb') as f:
            pkl.dump(projected_w_steps[-1, :1], f)

        # Render debug output: optional video and projected image and W vector.
        os.makedirs(outdir, exist_ok=True)
        if save_video:
            video_name = os.path.join(outdir, out_name + '.mp4')
            video = imageio.get_writer(video_name, mode='I', fps=10, codec='libx264', bitrate='16M')
            print (f'Saving optimization progress video "{video_name}"')
            for projected_w in projected_w_steps:
                synth_image = G.synthesis(projected_w.unsqueeze(0), noise_mode='const')
                synth_image = (synth_image + 1) * (255/2)
                synth_image = synth_image.permute(0, 2, 3, 1).clamp(0, 255).to(torch.uint8)[0].cpu().numpy()
                video.append_data(np.concatenate([target_uint8, synth_image], axis=1))
            video.close()

        # Save final projected image.
        img_path = os.path.join(outdir, out_name + '.png')
        projected_w = projected_w_steps[-1]
        synth_image = G.synthesis(projected_w.unsqueeze(0), noise_mode='const')
        synth_image = (synth_image + 1) * (255/2)
        synth_image = synth_image.permute(0, 2, 3, 1).clamp(0, 255).to(torch.uint8)[0].cpu().numpy()
        PIL.Image.fromarray(synth_image, 'RGB').save(img_path)

    @classmethod
    def run_projection_on_file(
        cls,
        network_pkl : str,
        file_path : str,
        out_folder : str,
        save_video : bool = False,
        num_steps : int = 2000,
        verbose : bool = False
    ):
        file_name = os.path.basename(file_path)

        print("File name:", file_name)
        
        if imghdr.what(file_path) is None:
            print(f'File {file_path} is not an image. Skipping it...')
            return

        print('Running projection on ' + file_path)
        Stylegan2Wrapper.run_project(
            network_pkl = network_pkl,
            target_fname = file_path,
            outdir = out_folder,
            save_video = save_video,
            num_steps = num_steps,
            out_name = file_name,
            verbose = verbose
        )