import os

class Config:
    REDIS_ROUTE = os.getenv('REDIS_ROUTE', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

    ALIS_ROUTE = os.getenv('ALIS_ROUTE', 'alis')
    ALIS_PORT = int(os.getenv('ALIS_PORT', 5000))

    STYLEGAN2_ROUTE = os.getenv('STYLEGAN2_ROUTE', 'stylegan2')
    STYLEGAN2_PORT = int(os.getenv('STYLEGAN2_PORT', 5001))

    SUPERRESOLUTION_ROUTE = os.getenv('SUPERRESOLUTION_ROUTE', 'superresolution')
    SUPERRESOLUTION_PORT = int(os.getenv('SUPERRESOLUTION_PORT', 5002))
