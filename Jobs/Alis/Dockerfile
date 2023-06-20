FROM base_cuda:latest

WORKDIR /app/

COPY . .

RUN "./install.sh"

EXPOSE 5000

CMD ["python3","api.py"]