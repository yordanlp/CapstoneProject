FROM base_cuda:latest

WORKDIR /app/

COPY . .

# Clone stylegan2 repository
RUN git clone https://github.com/NVlabs/stylegan2-ada-pytorch
RUN mv stylegan2-ada-pytorch stylegan2

# Create environment
RUN conda env create -f environment.yml

# Activate conda environment
RUN echo "source activate stylegan2-ada-pytorch" > ~/.bashrc
ENV PATH /opt/conda/envs/stylegan2-ada-pytorch/bin:$PATH

EXPOSE 5001

CMD ["python3", "api.py"]






