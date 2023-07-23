#%%
import os
import sys

import PIL
from PIL import Image

import torch

# TODO: to remove 
# CWD = '/home/erne/Desktop/Capstone/CapstoneProject/Jobs/Stylegan2/'
# os.chdir(CWD)
# stylegan2_path = os.path.abspath('./stylegan2')
# sys.path.append(stylegan2_path)
# -------------------------

from stylegan2 import dnnlib
from stylegan2 import legacy

def get_network_generator(
    network_pkl : str,
    device : torch.device = torch.device('cuda')
):
    print('Loading networks from "%s"...' % network_pkl)
    with dnnlib.util.open_url(network_pkl) as fp:
        G = legacy.load_network_pkl(fp)['G_ema'].requires_grad_(False).to(device) # type: ignore
    return G

def get_image_from_w(G, ws, device=torch.device('cuda')):
    return G.synthesis(ws, noise_mode='const').detach()

def prepare_img(img):
    img = (img + 1) * (255/2)
    img = img.permute(0, 2, 3, 1).clamp(0, 255).to(torch.uint8)[0].cpu().numpy()
    return img

def save_img(img, path):
    img = prepare_img(img)
    PIL.Image.fromarray(img, 'RGB').save(path)

# from config import models_config

# for model in models_config.keys():
#     print(model)
#     network_pkl = models_config[model]['checkpoint']
#     G = get_network_generator(network_pkl)
#     print(G.img_resolution)
#     print(G.num_ws, end='\n\n')

# # image = prepare_img(get_images_from_z(network_pkl, 1))

# # import cv2

# # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# # cv2.imwrite('/home/erne/Desktop/a.png', image)
# # help(cv2.imwrite)
