git clone https://github.com/universome/alis

pip install flask omegaconf numpy==1.19


yes | conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia 
yes | conda install -c conda-forge imageio imageio-ffmpeg omegaconf
yes | conda install -c anaconda flask
yes | conda install -c anaconda scikit-learn
yes | conda install -c conda-forge ninja
yes | conda install -c conda-forge opencv

conda deactivate

echo "Activate the environment by running **conda activate alis**"
