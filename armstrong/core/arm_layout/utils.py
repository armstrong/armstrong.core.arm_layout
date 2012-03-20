# Here for backwards compatibility (deprecated)
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from armstrong.utils.backends import GenericBackend

render_model = (GenericBackend("ARMSTRONG_RENDER_MODEL_BACKEND",
        defaults="armstrong.core.arm_layout.backends.BasicRenderModelBackend")
    .get_backend())

# Here for backwards compatibility (deprecated)
get_layout_template_name = render_model.get_layout_template_name
