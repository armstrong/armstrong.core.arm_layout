from django import template
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
        return render_model(object, name, context_instance=context)


@register.tag(name="render_model")
def do_render_model(parser, token):
    tokens = token.split_contents()
    if len(tokens) is 3:
        _, object, name = tokens
        return RenderObjectNode(object, name)

    message = "Too %s parameters" % ("many" if len(tokens) > 3 else "few")
    raise TemplateSyntaxError(message)


class RenderListNode(template.Node):
    def __init__(self, obj_list, name):
        self.obj_list = obj_list
        self.name = template.Variable(name)

    def render(self, context):
        name = self.name.resolve(context)
        obj_list = self.obj_list.resolve(context)
        return ''.join(render_model(obj,
                                    name,
                                    context_instance=context)
                            for obj in obj_list)


@register.tag(name="render_list")
def do_render_list(parser, token):
    tokens = token.split_contents()
    if len(tokens) is 3:
        _, obj_list, name = tokens
        obj_list = parser.compile_filter(obj_list)
        return RenderListNode(obj_list, name)

    message = "Too %s parameters" % ("many" if len(tokens) > 3 else "few")
    raise TemplateSyntaxError(message)


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


class RenderNextNode(template.Node):
    def __init__(self, name):
        self.name = template.Variable(name)

    def render(self, context):
        obj = context['iter'].next()
        name = self.name.resolve(context)
        return render_model(obj, name, context_instance=context)


@register.tag
def render_next(parser, token):
    tokens = token.split_contents()
    if len(tokens) is 2:
        _, name = tokens
        return RenderNextNode(name)

    message = "Too %s parameters" % ("many" if len(tokens) > 2 else "few")
    raise TemplateSyntaxError(message)


class RenderRemainderNode(template.Node):
    def __init__(self, name):
        self.name = template.Variable(name)

    def render(self, context):
        name = self.name.resolve(context)
        result = []
        try:
            while True:
                obj = context['iter'].next()
                result.append(
                    render_model(obj, name, context_instance=context))
        except StopIteration:
            return ''.join(result)


@register.tag
def render_remainder(parser, token):
    tokens = token.split_contents()
    if len(tokens) is 2:
        _, name = tokens
        return RenderRemainderNode(name)

    message = "Too %s parameters" % ("many" if len(tokens) > 2 else "few")
    raise TemplateSyntaxError(message)
