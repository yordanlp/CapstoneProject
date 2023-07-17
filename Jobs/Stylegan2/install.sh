#!/bin/bash -i

# Clone stylegan2-ada-pytorch
git clone https://github.com/NVlabs/stylegan2-ada-pytorch
mv stylegan2-ada-pytorch stylegan2

echo "Cloning done"

#create environment
conda env create -f environment.yml
conda activate stylegan2-ada-pytorch

yes | conda install -c anaconda requests
yes | conda install -c anaconda click
yes | conda install -c anaconda scikit-learn
yes | conda install -c conda-forge imageio
yes | conda install -c conda-forge imageio-ffmpeg

conda deactivate

echo "Ativate your environment with **conda activate stylegan2-ada-pytorch**"
