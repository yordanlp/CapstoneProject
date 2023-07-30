docker build -f BaseCuda.dockerfile -t base_cuda .
docker build -f Alis/Dockerfile -t alis Alis/.
docker build -f Stylegan2/Dockerfile -t stylegan2 Stylegan2/.
docker build -f Worker/Dockerfile -t worker Worker/.

docker build -f Superresolution/environment.dockerfile -t superresolution_env Superresolution/.
docker build -f Superresolution/Dockerfile -t superresolution Superresolution/.