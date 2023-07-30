FROM base_cuda:latest

COPY environment.yml .

# Install environment
RUN conda env create -f environment.yml 

RUN /bin/bash -c 'source activate superresolution && \ 
                pip3 install -e "git+https://github.com/CompVis/taming-transformers.git@master#egg=taming-transformers" && \
                pip3 install -e "git+https://github.com/openai/CLIP.git@main#egg=clip"'

# Clean cache
RUN conda clean -ay

# Activate conda environment
RUN echo "source activate superresolution" > ~/.bashrc
ENV PATH /opt/conda/envs/superresolution/bin:$PATH