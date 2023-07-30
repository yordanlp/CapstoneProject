FROM alis_env:latest

WORKDIR /app/

COPY . .

# Clone alis repository
RUN git clone https://github.com/universome/alis

EXPOSE 5000

CMD ["python3","api.py"]