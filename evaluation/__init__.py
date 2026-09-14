def evaluate(*args, **kwargs):
    from .check import evaluate as implementation
    return implementation(*args, **kwargs)


__all__ = ["evaluate"]
