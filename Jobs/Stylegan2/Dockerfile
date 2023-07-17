FROM base_cuda:latest

WORKDIR /app/

COPY . .

RUN conda env create -f environment2.yml

RUN echo "source activate stylegan2-ada-pytorch_v2" > ~/.bashrc
ENV PATH /opt/conda/envs/alis/bin:$PATH






