import os

root_path = os.path.dirname(os.path.abspath(__file__))

class Config:
    DEBUG = False
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = f"{ROOT_PATH}/images"
    OUTPUT_PROJECTION = f"{ROOT_PATH}/projection"
    OUTPUT_PCA = f"{ROOT_PATH}/pca"

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

