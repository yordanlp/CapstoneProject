FROM base_cuda:latest

# Copy env file
COPY environment.yml .

# Create environment
RUN conda env create -f environment.yml

# Clean cache
RUN conda clean -ay

# Activate conda environment
RUN echo "source activate stylegan2-ada-pytorch" > ~/.bashrc
ENV PATH /opt/conda/envs/stylegan2-ada-pytorch/bin:$PATH





