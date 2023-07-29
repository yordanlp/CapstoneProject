FROM stylegan2_env:latest

WORKDIR /app/

COPY . .

# Clone stylegan2 repository
RUN git clone https://github.com/NVlabs/stylegan2-ada-pytorch
RUN mv stylegan2-ada-pytorch stylegan2

EXPOSE 5001

CMD ["python3", "api.py"]






