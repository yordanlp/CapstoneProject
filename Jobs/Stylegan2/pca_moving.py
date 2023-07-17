'''
Usage example 

python pca_moving.py --inp_folder data/in/ --out_folder data/out/ \
	--network_checkpoint https://nvlabs-fi-cdn.nvidia.com/stylegan2/networks/stylegan2-church-config-f.pkl \
	--interpolation_steps 40 --latent_edits 1,6,8,-5,5 15,4,5,-2,2
 
With previous commands the script will create 40 images in the movement process
and will move in 1st principal component from style layer from 6 to 8 and movement coefficients will range from -5 to 5
as well as the 15th principal component from style layer from 4 to 5 and movement coefficients will range from -2 to 2

Note: For parsing purposes, don't leave spaces between numbers in the same latent_edits items

Important: Take into account that the amount of style layers may be different for different checkpoints. 
	(ie: This may give you an error if you pass layer 16 as parameter using a checkpoint with 13 style layers)
'''

import os
import numpy as np
import PIL.Image
import torch
import torch.nn.functional as F
import pickle as pkl
import argparse
from sklearn.decomposition import PCA
import sys

sys.path.insert(1, os.path.join(os.getcwd(), 'stylegan2'))

from stylegan2 import legacy
from stylegan2 import dnnlib

def get_network(
	network_pkl : str,
	device : torch.device = torch.device('cuda'),
):
	with dnnlib.util.open_url(network_pkl) as fp:
		G = legacy.load_network_pkl(fp)['G_ema'].requires_grad_(False).to(device) # type: ignore
	return G

def save_img(img, path):
	img = (img + 1) * (255/2)
	img = img.permute(0, 2, 3, 1).clamp(0, 255).to(torch.uint8)[0].cpu().numpy()
	PIL.Image.fromarray(img, 'RGB').save(path)

def move(
	network_pkl : str,       #Check point
	interpolation_steps,    #amount of interpolation samples
	outdir : str, 
	w : torch.tensor        = None, # if w is None its randomly sampled a point on Z space to perform movement 
	device : torch.device   = torch.device('cuda'),
	n_samples : int         = 10000, #number of samples to compute pca
	fit_pca : bool          = True, #whether to compute pca or if it's already calculated
	modify_list : list      = [], #each item is a tuple of the form (principal_component_number, (start_layer, end_layer), (lower_coeff_limit, upper_coeff_limit))
):
	G = get_network(network_pkl=network_pkl, device=device)
	G.eval()
	
	pca_path = os.path.join(outdir, '..', 'pca.pkl')

	if fit_pca:
		zs = torch.randn([n_samples, G.z_dim], device=device)
		ws = G.mapping(zs, c=None)[:, 0, :].detach().cpu().numpy()      
		pca = PCA(n_components=G.w_dim).fit(ws)
		with open(pca_path, 'wb') as f:
			pkl.dump(pca, f)
	else:
		with open(pca_path, 'rb') as f:
			pca = pkl.load(f)

	if w is None:
		z = torch.randn([1, G.z_dim], device=device)
		w = G.mapping(z, c=None)[:, 0, :]#torch.nn.functional.one_hot(torch.tensor([cur_class]), n_classes).to(device))
	
	ws = w.unsqueeze(0).repeat([interpolation_steps, 1, G.num_ws, 1])

	for (comp, (l_layer, r_layer), (l_coeff, r_coeff)) in modify_list:
		v = np.zeros((1, G.w_dim))
		v[0, comp] = 1
		u = pca.inverse_transform(v) - pca.mean_
		n_layers = r_layer - l_layer + 1
		u = torch.tensor(u, device=device)#.unsqueeze(0).repeat([2, n_layers, 1])

		coeff = torch.linspace(l_coeff, r_coeff, interpolation_steps, device=device).reshape(interpolation_steps, 1, 1, 1).repeat([1, 1, n_layers, G.w_dim])		
		mov = coeff * u

		ws[:, :, l_layer:r_layer+1, :] += mov

	os.makedirs(outdir, exist_ok=True)

	for i in range(interpolation_steps):
		img = G.synthesis(ws[i], noise_mode='const')
		save_img(img, os.path.join(outdir, f'{i}.jpg'))


def edit_item(s):
	try:
		s1 = s.split(',')
		comp = int(s1[0])
		l_layer = int(s1[1])
		r_layer = int(s1[2])
		l_coeff = float(s1[3])
		r_coeff = float(s1[4])
		return (comp, (l_layer, r_layer), (l_coeff, r_coeff))
	except:
		raise argparse.ArgumentTypeError("tuples must be comp,l_layer,r_layer,l_coeff,r_coeff (No spaces)")

def run_pca_moving_on_folder(
	network_pkl: str,
	inp_folder: str,
	out_folder: str,
	interpolation_steps: int,
	latent_edits: list
):
	fit_pca = True

	files = os.listdir(inp_folder)

	for idx, file in enumerate(files):
		file_name, ext = file.split('.')
		target_fname = os.path.join(inp_folder, file)

		if ext != 'pkl':
			print(f'File {target_fname} is not a pickle file. Skipping it...')
			continue
		
		with open(target_fname, 'rb') as f:
			w = pkl.load(f)
		outdir = os.path.join(out_folder, file_name)
		os.makedirs(outdir, exist_ok=True)

		move(
			network_pkl = network_pkl,
			interpolation_steps = interpolation_steps,
			outdir = outdir,
			w = w,
			modify_list = latent_edits,
			fit_pca = fit_pca
		)

		fit_pca = False


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Move in latent space of images in given folder')
	parser.add_argument('--inp_folder', help='folder containing latents in pickle files', required=True)
	parser.add_argument('--out_folder', help='folder to store images after movements', required=True)
	parser.add_argument('--network_checkpoint', help='url with the pretrained network', required=True)
	parser.add_argument('--interpolation_steps', help='amount of steps in the moving', required=True, type=int)
	parser.add_argument('--latent_edits', help='list containing tuple principal_component_number,start_layer,end_layer,lower_coeff_limit,upper_coeff_limit', type=edit_item, nargs='+', required=True)  
	
	args = parser.parse_args()
	
	run_pca_moving_on_folder(
		network_pkl = args.network_checkpoint, 
		inp_folder = args.inp_folder,
		out_folder = args.out_folder,
		interpolation_steps = args.interpolation_steps,
		latent_edits = args.latent_edits
	)






