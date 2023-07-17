'''
Usage example
python runProjectAndMove.py --inp_folder ~/Desktop/input --out_folder ~/Desktop/output  \
    --network_checkpoint https://nvlabs-fi-cdn.nvidia.com/stylegan2/networks/stylegan2-church-config-f.pkl \
    --interpolation_steps 40 --latent_edits  15,7,10,-15,15

By default the projection is ran on 2000 steps, to change it, specify parameter 
    --projection_steps NUM_STEPS

To show the loss at each projection step use 
    --verbose

To save a video with the whole projection process use
    --save_video

With previous commands the script will create 40 images in the movement process
and will move in 15th principal component from style layer from 7 to 10 and movement coefficients will range from -15 to 15

Note: For parsing purposes, don't leave spaces between numbers in the same latent_edits item


Urls with different pretrained networks:

https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/
https://nvlabs-fi-cdn.nvidia.com/stylegan2/networks/

Pick the one you want and put into the parameter --network_checkpoint

Important: Take into account that the amount of style layers may be different for different checkpoints. 
	(ie: This may give you an error if you pass layer 16 as parameter using a checkpoint with 13 style layers)
'''

import os
import argparse

from projector import run_projection_on_folder
from pca_moving import run_pca_moving_on_folder, edit_item

import sys
sys.path.insert(1, os.path.join(os.getcwd(), 'stylegan2'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Project and move latents for images in given directory')
    parser.add_argument('--inp_folder', help='folder containing the images', required=True)
    parser.add_argument('--out_folder', help='folder to store the moves', required=True)
    parser.add_argument('--network_checkpoint', help='url with the pretrained network', required=True)
    parser.add_argument('--interpolation_steps', help='amount of steps in the moving', required=True, type=int)
    parser.add_argument('--latent_edits', help='list containing tuple principal_component_number,start_layer,end_layer,lower_coeff_limit,upper_coeff_limit', type=edit_item, nargs='+', required=True)  
    parser.add_argument('--projection_steps', help='amount of epochs for projection', required=False, default=2000, type=int)
    parser.add_argument('--verbose', help='print projection log', action='store_true')
    parser.add_argument('--save_video', help='save video of all epoch projections', action='store_true')

    args = parser.parse_args()

    projected_folder = os.path.join(args.out_folder, 'projected_images')
    os.makedirs(projected_folder, exist_ok=True)

    print('Folder containing images to project and move: ' + args.inp_folder)
    print('Folder containing projected images: ' + projected_folder)
    print('Folder containing final images with moves: ' + args.out_folder)

    print('Starting projection process...')
    run_projection_on_folder(
        network_pkl = args.network_checkpoint,
        inp_folder = args.inp_folder,
        out_folder = projected_folder,
        save_video = args.save_video,
        num_steps = args.projection_steps,
        verbose = args.verbose 
    )
    print('Done with projections!')

    print('Starting moving process...')
    run_pca_moving_on_folder(
        network_pkl = args.network_checkpoint,
        inp_folder = projected_folder,
        out_folder = args.out_folder, 
        interpolation_steps = args.interpolation_steps,
        latent_edits = args.latent_edits
    )
    print('Done!!!')
