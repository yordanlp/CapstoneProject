'''
Usage example
python projector.py --inp_folder ~/Desktop/input --out_folder ~/Desktop/output \
    --network_checkpoint https://nvlabs-fi-cdn.nvidia.com/stylegan2/networks/stylegan2-church-config-f.pkl

By default the projection is ran on 2000 steps, to change it, specify parameter 
    --num_steps NUM_STEPS

To show the loss at each step use
    --verbose

To save a video with the whole projection process use
    --save_video
'''

import copy
import os
from turtle import st
import imageio
import imghdr
import numpy as np
import PIL.Image
import torch
import torch.nn.functional as F
import argparse
import pickle as pkl
from time import perf_counter
import sys

sys.path.insert(1, os.path.join(os.getcwd(), 'stylegan2'))

from stylegan2 import dnnlib
from stylegan2 import legacy

def load_network(
    network_pkl : str,
    device : torch.device
):
    print('Loading networks from "%s"...' % network_pkl)
    with dnnlib.util.open_url(network_pkl) as fp:
        G = legacy.load_network_pkl(fp)['G_ema'].requires_grad_(False).to(device) # type: ignore
    return G


def project(
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


def run_projection(
    network_pkl: str,
    target_fname: str,
    outdir: str,
    out_name : str,
    num_steps: int,
    save_video: bool       = False,
    seed: int              = 123,
    device : torch.device  = torch.device('cuda'),
    verbose : bool         = False
):
    np.random.seed(seed)
    torch.manual_seed(seed)
    G = load_network(network_pkl, device)
    
    # Load target image.
    target_pil = PIL.Image.open(target_fname).convert('RGB')
    w, h = target_pil.size
    s = min(w, h)
    target_pil = target_pil.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    target_pil = target_pil.resize((G.img_resolution, G.img_resolution), PIL.Image.LANCZOS)
    target_uint8 = np.array(target_pil, dtype=np.uint8)

    # Optimize projection.
    start_time = perf_counter()
    projected_w_steps = project(
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

def run_projection_on_folder(
    network_pkl : str,
    inp_folder : str,
    out_folder : str,
    save_video : bool = False,
    num_steps : int = 2000,
    verbose : bool = False
):
    files = os.listdir(inp_folder)

    for file in files:
        file_name, ext = file.split('.')
        target_fname = os.path.join(inp_folder, file)
        
        if imghdr.what(target_fname) is None:
            print(f'File {target_fname} is not an image. Skipping it...')
            continue

        print('Running projection on ' + target_fname)
        run_projection(
            network_pkl = network_pkl,
            target_fname = target_fname,
            outdir = out_folder,
            save_video = save_video,
            num_steps = num_steps,
            out_name = file_name,
            verbose = verbose
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Project Images in given directory')
    parser.add_argument('--inp_folder', help='folder containing images', required=True)
    parser.add_argument('--out_folder', help='folder to store projections', required=True)
    parser.add_argument('--network_checkpoint', help='url with the pretrained network', required=True)
    parser.add_argument('--num_steps', help='amount of epochs', required=False, default=2000, type=int)
    parser.add_argument('--verbose', help='print log', action='store_true')
    parser.add_argument('--save_video', help='save video of all epoch projections', action='store_true')
    args = parser.parse_args()

    run_projection_on_folder(
        network_pkl = args.network_checkpoint,
        inp_folder = args.inp_folder,
        out_folder = args.out_folder,
        save_video = args.save_video,
        num_steps = args.num_steps,
        verbose = args.verbose 
    )    
