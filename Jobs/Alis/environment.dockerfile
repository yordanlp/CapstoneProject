FROM base_cuda:latest

# Copy env file
COPY environment.yml .

# Create environment
RUN conda env create -f environment.yml

# Clean cache
RUN conda clean -ay

# Activate conda environment
RUN echo "source activate alis" > ~/.bashrc
ENV PATH /opt/conda/envs/alis/bin:$PATH
