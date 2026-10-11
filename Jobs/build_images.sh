docker build -f BaseCuda.dockerfile -t base_cuda .

# ALIS is disabled: its checkpoint (lhq1024-snapshot.pkl) is no longer publicly available
# docker build -f Alis/environment.dockerfile -t alis_env Alis/.
# docker build -f Alis/Dockerfile -t alis Alis/.

docker build -f Stylegan2/environment.dockerfile -t stylegan2_env Stylegan2/.
docker build -f Stylegan2/Dockerfile -t stylegan2 Stylegan2/.

docker build -f Superresolution/environment.dockerfile -t superresolution_env Superresolution/.
docker build -f Superresolution/Dockerfile -t superresolution Superresolution/.

docker build -f Worker/Dockerfile -t worker Worker/.
