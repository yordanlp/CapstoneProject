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

class Config:
    DEBUG = False
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
    SHARED_FOLDER = os.getenv('SHARED_FOLDER', f"{ROOT_PATH}/Shared")
    UPLOAD_FOLDER = f"{SHARED_FOLDER}/images"
    OUTPUT_PROJECTION = f"{SHARED_FOLDER}/projection"
    OUTPUT_PCA = f"{SHARED_FOLDER}/pca"
    UPSCALED_FOLDER = f"{SHARED_FOLDER}/upscaled"

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

