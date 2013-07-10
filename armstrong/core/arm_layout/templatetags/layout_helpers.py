from django import template
from django.template.base import TemplateSyntaxError

from ..utils import render_model as render_model_backend

register = template.Library()


class RenderObjectNode(template.Node):
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name

    def render(self, context):
        name = self.name.resolve(context)
        obj = self.obj.resolve(context)
        return render_model_backend(obj, name, context_instance=context)


@register.tag(name="render_model")
def do_render_model(parser, token):
    tokens = token.split_contents()
    if len(tokens) is 3:
        _, obj, name = tokens
        obj = parser.compile_filter(obj)
        name = parser.compile_filter(name)
        return RenderObjectNode(obj, name)

    message = "Too %s parameters" % ("many" if len(tokens) > 3 else "few")
    raise TemplateSyntaxError(message)


@register.simple_tag(takes_context=True)
def render_list(context, obj_list, template_name):
    return ''.join(
        render_model_backend(obj, template_name, context_instance=context)
            for obj in obj_list)


class RenderIterNode(template.Node):
    def __init__(self, obj_list, nodelist_contents):
        self.obj_list = obj_list
        self.nodelist_contents = nodelist_contents

    def render(self, context):
        context.push()
        objs = self.obj_list.resolve(context)
        context['iter'] = iter(objs)
        nodelist = template.NodeList()
        try:
            for node in self.nodelist_contents:
                nodelist.append(node.render(context))
        except StopIteration:
            pass
        context.pop()
        return nodelist.render(context)


@register.tag
def render_iter(parser, token):
    tokens = token.split_contents()
    if len(tokens) is 2:
        _, obj_list = tokens
        obj_list = parser.compile_filter(obj_list)
        nodelist_contents = parser.parse(('endrender_iter', ))
        parser.delete_first_token()
        return RenderIterNode(obj_list, nodelist_contents)

    message = "Too %s parameters" % ("many" if len(tokens) > 2 else "few")
    raise TemplateSyntaxError(message)


@register.simple_tag(takes_context=True)
def render_next(context, template_name):
    obj = context['iter'].next()
    return render_model_backend(obj, template_name, context_instance=context)


@register.simple_tag(takes_context=True)
def render_remainder(context, template_name):
    result = []
    try:
        while True:
            obj = context['iter'].next()
            result.append(
                render_model_backend(obj, template_name, context_instance=context))
    except StopIteration:
        pass
    return ''.join(result)
