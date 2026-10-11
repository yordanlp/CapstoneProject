import os

root_path = os.path.dirname(os.path.abspath(__file__))


def get_device():
    # DEVICE can be 'auto' (default), 'cuda', 'mps' or 'cpu'
    import torch
    requested = os.getenv('DEVICE', 'auto').lower()
    if requested != 'auto':
        return torch.device(requested)
    if torch.cuda.is_available():
        return torch.device('cuda')
    if torch.backends.mps.is_available():
        return torch.device('mps')
    return torch.device('cpu')

DEVICE = get_device()

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
    SHARED_FOLDER = os.getenv('SHARED_FOLDER', f"{ROOT_PATH}/Shared")
    UPLOAD_FOLDER = f"{SHARED_FOLDER}/images"
    OUTPUT_PROJECTION = f"{SHARED_FOLDER}/projection"
    OUTPUT_PCA = f"{SHARED_FOLDER}/pca"

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

