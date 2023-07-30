FROM superresolution_env:latest

WORKDIR /app/

COPY . .

# Clone repo
RUN git clone https://github.com/CompVis/latent-diffusion.git

RUN /bin/bash -c 'source activate superresolution && \ 
                pip3 install -e latent-diffusion/.'

EXPOSE 5002

CMD ["python3","api.py"]