from .basic import BasicLayoutBackend


class ModelProvidedLayoutBackend(BasicLayoutBackend):
    def get_layout_template_name(self, model_obj, name):
        if hasattr(model_obj, "get_layout_template_name"):
            return model_obj.get_layout_template_name(name)

        return super(ModelProvidedLayoutBackend, self)\
            .get_layout_template_name(model_obj, name)
