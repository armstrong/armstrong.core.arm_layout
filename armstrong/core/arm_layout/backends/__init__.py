from .basic import BasicLayoutBackend
from .model_provided import ModelProvidedLayoutBackend


# DEPRECATED: To be removed in ArmLayout 2.0
import warnings


class BasicRenderModelBackend(BasicLayoutBackend):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        msg = "BasicRenderModelBackend is deprecated and will be removed in ArmLayout 2.0. Use BasicLayoutBackend."
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        super(BasicRenderModelBackend, self).__init__(*args, **kwargs)
