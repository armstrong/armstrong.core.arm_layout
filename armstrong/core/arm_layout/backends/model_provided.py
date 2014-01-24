from .basic import BasicLayoutBackend


class ModelProvidedLayoutBackend(BasicLayoutBackend):
    """
    Allow models to specify their own template lookup.

    Use this backend to allow models to look up their own templates
    by implementing a `get_layout_template_name` method. Any model
    without that method just falls back to the default model
    inheritance lookup structure so this is essentially a drop-in
    replacement for BasicLayoutBackend.

    """
    def get_layout_template_name(self, model_obj, name):
        if hasattr(model_obj, "get_layout_template_name"):
            return model_obj.get_layout_template_name(name)

        return super(ModelProvidedLayoutBackend, self)\
            .get_layout_template_name(model_obj, name)
