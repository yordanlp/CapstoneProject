'''
Usage example

python generate_random_image.py --network_checkpoint https://nvlabs-fi-cdn.nvidia.com/stylegan2/networks/stylegan2-church-config-f.pkl \
        --n_samples 2 --out_folder data/in/
'''

import os
import numpy as np
import PIL.Image
import torch
import torch.nn.functional as F
import pickle as pkl
import argparse
import sys

sys.path.insert(1, os.path.join(os.getcwd(), 'stylegan2'))

from stylegan2 import legacy
from stylegan2 import dnnlib

def load_network(
    network_pkl : str,
    device : torch.device = torch.device('cuda')
):
    print('Loading networks from "%s"...' % network_pkl)
    with dnnlib.util.open_url(network_pkl) as fp:
        G = legacy.load_network_pkl(fp)['G_ema'].requires_grad_(False).to(device) # type: ignore
    return G

def generate(
    network_pkl: str,
    n_samples : int,
    device : torch.device = torch.device('cuda'),
):
    G = load_network(network_pkl, device)
    z_samples = torch.randn((n_samples, G.z_dim), device=device)
    ws = G.mapping(z_samples, None)
    synth_images = G.synthesis(ws, noise_mode='const')
    
    return synth_images

def save_images(synth_images: torch.tensor, outdir : str):
    os.makedirs(outdir, exist_ok=True)
    for idx in range(synth_images.shape[0]):
        synth_image = synth_images[idx, :, :, :].unsqueeze(0)
        synth_image = (synth_image + 1) * (255/2)
        synth_image = synth_image.permute(0, 2, 3, 1).clamp(0, 255).to(torch.uint8)[0].cpu().numpy()
        out_path = os.path.join(outdir, f'{idx}.png')
        PIL.Image.fromarray(synth_image, 'RGB').save(out_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate random image from stylegan2 checkpoint')
    parser.add_argument('--network_checkpoint', help='url with the pretrained network', required=True)
    parser.add_argument('--n_samples', help='amount of images to generate', default=1, type=int)
    parser.add_argument('--out_folder', help='folder to store images after movements', required=True)
    
    args = parser.parse_args()

    synth_images = generate(
        network_pkl = args.network_checkpoint,
        n_samples = args.n_samples,
    )

    save_images(synth_images, args.out_folder)

