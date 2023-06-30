# Use the latest Ubuntu as a base image
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Update system packages and install prerequisites
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    sudo \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    wget

# Set the CUDA_HOME environment variable
ENV CUDA_HOME=/usr/local/cuda

# Install Anaconda
ENV ANACONDA_VERSION=2023.03-1
RUN wget https://repo.anaconda.com/archive/Anaconda3-${ANACONDA_VERSION}-Linux-x86_64.sh && \
    bash Anaconda3-${ANACONDA_VERSION}-Linux-x86_64.sh -b -p /opt/conda && \
    rm Anaconda3-${ANACONDA_VERSION}-Linux-x86_64.sh

# Set path to conda
ENV PATH /opt/conda/bin:$PATH
