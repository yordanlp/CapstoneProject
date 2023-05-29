from app import db
from .db_helper import model_to_dict

def object_to_dict(obj):
    if isinstance(obj, list):
        return [object_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: object_to_dict(value) for key, value in obj.items()}
    elif isinstance(obj, db.Model):
        return model_to_dict(obj)
    elif hasattr(obj, "__dict__"):
        return object_to_dict(vars(obj))
    else:
        return obj