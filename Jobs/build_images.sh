docker build -f BaseCuda.dockerfile -t base_cuda .
docker build -f Alis/Dockerfile -t alis Alis/.
docker build -f Worker/Dockerfile -t worker Worker/.