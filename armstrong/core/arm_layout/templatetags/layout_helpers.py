from contextlib import contextmanager
import copy
from django import template
from django.template import RequestContext
from django.template.base import TemplateSyntaxError

from ..utils import render_model

register = template.Library()


class RenderObjectNode(template.Node):
    def __init__(self, object, name):
        self.object = template.Variable(object)
        self.name = template.Variable(name)

    def render(self, context):
        name = self.name.resolve(context)
        object = self.object.resolve(context)
        return render_model(object, name, dictionary={},
            context_instance=context)


@register.tag(name="render_model")
def do_render_model(parser, token):
    tokens = token.split_contents()
    if len(tokens) is 3:
        _, object, name = tokens
        name_is_string = ('"' in name)
        return RenderObjectNode(object, name)

    message = "Too %s parameters" % ("many" if len(tokens) > 3 else "few")
    raise TemplateSyntaxError(message)
