class ModelHandle:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        self.loaded = model_path is not None


def load_model(model_path: str | None = None) -> ModelHandle:
    return ModelHandle(model_path=model_path)
