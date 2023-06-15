import torch
import sys
import numpy as np
import os
import PIL
from PIL import Image

from alis import dnnlib
from alis.scripts import legacy
from alis.training.networks import SynthesisLayer

def get_network_generator(
    network_pkl = 'https://kaust-cair.s3.amazonaws.com/alis/lhq1024-snapshot.pkl',
    device      = torch.device('cuda')
):
    print('Loading networks from "%s"...' % network_pkl)
    device = torch.device('cuda')
    with dnnlib.util.open_url(network_pkl) as fp:
        data = legacy.load_network_pkl(fp) 
        G = data['G_ema'].requires_grad_(False).to(device) # type: ignore
    return G

def get_network_discriminator(
    network_pkl = 'https://kaust-cair.s3.amazonaws.com/alis/lhq1024-snapshot.pkl',
    device      = torch.device('cuda')
):
    print('Loading networks from "%s"...' % network_pkl)
    device = torch.device('cuda')
    with dnnlib.util.open_url(network_pkl) as fp:
        data = legacy.load_network_pkl(fp) 
        D = data['D'].requires_grad_(False).to(device) # type: ignore
    return D

def get_image_from_w_alis(G, ws, device=torch.device('cuda')):
    curr_idx = 1
    curr_ws = ws[curr_idx].unsqueeze(0)
    left_ws = ws[curr_idx - 1].unsqueeze(0)
    right_ws = torch.zeros_like(curr_ws).to(device)
    curr_ws_context = torch.stack([left_ws, right_ws], dim=1)
    left_borders_idx=torch.tensor([0], requires_grad=False).to(device)

    synth_images = G.synthesis(curr_ws, ws_context=curr_ws_context, left_borders_idx=left_borders_idx, noise_mode='const')
    return synth_images.detach()

def prepare_img(img):
    img = (img + 1) * (255/2)
    img = img.permute(0, 2, 3, 1).clamp(0, 255).to(torch.uint8)[0].cpu().numpy()
    return img
    
def save_img(img, path):
    PIL.Image.fromarray(img, 'RGB').save(path)

