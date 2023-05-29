def model_to_dict(model):
    result = {}
    for column in model.__table__.columns:
        result[column.name] = getattr(model, column.name)
    return result