from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from .basic import BasicLayoutBackend
from .model_provided import ModelProvidedLayoutBackend


# DEPRECATED: To be removed in ArmLayout 2.0
import warnings


def deprecate(cls):
    def wrapper(*args, **kwargs):
        msg = "BasicRenderModelBackend is deprecated and will be removed in ArmLayout 2.0. Use %s."
        warnings.warn(msg % cls.__name__, DeprecationWarning, stacklevel=2)
        return cls(*args, **kwargs)
    return wrapper

BasicRenderModelBackend = deprecate(BasicLayoutBackend)
