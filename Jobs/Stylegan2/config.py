import os

root_path = os.path.dirname(os.path.abspath(__file__))

models_config = {
    'cars': {
        'checkpoint': 'https://nvlabs-fi-cdn.nvidia.com/stylegan2/networks/stylegan2-car-config-f.pkl',
        'layers': 16,
        'resolution': 512,
    },
    'faces': {
        'checkpoint': 'https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/ffhq.pkl',
        'layers': 18,
        'resolution': 1024,
    },
    'cats': {
        'checkpoint': 'https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/afhqcat.pkl',
        'layers': 16,
        'resolution': 512,
    },
    'dogs': {
        'checkpoint': 'https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/afhqdog.pkl',
        'layers': 16,
        'resolution': 512,
    },
    'wild': {
        'checkpoint': 'https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/afhqwild.pkl',
        'layers': 16,
        'resolution': 512,
    },
    'churches': {
        'checkpoint': 'https://nvlabs-fi-cdn.nvidia.com/stylegan2/networks/stylegan2-church-config-f.pkl',
        'layers': 14,
        'resolution': 256,
    },
}


class Config:
    DEBUG = False
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = f"{ROOT_PATH}/Shared/images"
    OUTPUT_PROJECTION = f"{ROOT_PATH}/Shared/projection"
    OUTPUT_PCA = f"{ROOT_PATH}/Shared/pca"

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

