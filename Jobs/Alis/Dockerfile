FROM base_cuda:latest

WORKDIR /app/

COPY . .

# Clone alis repository
RUN git clone https://github.com/universome/alis

# Create environment
RUN conda env create -f environment.yml

# Clean cache
RUN conda clean -ay

# Activate conda environment
RUN echo "source activate alis" > ~/.bashrc
ENV PATH /opt/conda/envs/alis/bin:$PATH

EXPOSE 5000

CMD ["python3","api.py"]