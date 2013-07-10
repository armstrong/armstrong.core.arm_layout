from django import template
from django.template.defaulttags import token_kwargs
from django.template.base import TemplateSyntaxError

from ..utils import render_model

register = template.Library()


class RenderObjectNode(template.Node):
    def __init__(self, obj, template_name, *args, **kwargs):
        self.obj = obj
        self.template_name = template_name
        self.extra_context = kwargs.pop('extra_context', {})
        self.isolated_context = kwargs.pop('isolated_context', False)
        super(RenderObjectNode, self).__init__(*args, **kwargs)

    def render_template(self, obj, template_name, context):
        values = dict([(name, var.resolve(context)) for name, var
                       in self.extra_context.iteritems()])
        if self.isolated_context:
            return render_model(obj, template_name, context_instance=context.new(values))
        context.update(values)
        output = render_model(obj, template_name, context_instance=context)
        context.pop()
        return output

    def render(self, context):
        obj = self.obj.resolve(context)
        template_name = self.template_name.resolve(context)
        return self.render_template(obj, template_name, context)


@register.tag(name="render_model")
def do_render_model(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("%r tag takes at least two arguments: the object and the name of the template to render it with." % bits[0])
    options = {}
    remaining_bits = bits[3:]
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option in options:
            raise TemplateSyntaxError('The %r option was specified more '
                                      'than once.' % option)
        if option == 'with':
            value = token_kwargs(remaining_bits, parser, support_legacy=False)
            if not value:
                raise TemplateSyntaxError('"with" in %r tag needs at least '
                                          'one keyword argument.' % bits[0])
        elif option == 'only':
            value = True
        else:
            raise TemplateSyntaxError('Unknown argument for %r tag: %r.' %
                                      (bits[0], option))
        options[option] = value
    isolated_context = options.get('only', False)
    namemap = options.get('with', {})
    return RenderObjectNode(
        parser.compile_filter(bits[1]),
        parser.compile_filter(bits[2]),
        extra_context=namemap,
        isolated_context=isolated_context)


class RenderListNode(template.Node):
    def __init__(self, obj_list, name):
        self.obj_list = obj_list
        self.name = name

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
        name = parser.compile_filter(name)
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
        self.name = name

    def render(self, context):
        obj = context['iter'].next()
        name = self.name.resolve(context)
        return render_model(obj, name, context_instance=context)


@register.tag
def render_next(parser, token):
    tokens = token.split_contents()
    if len(tokens) is 2:
        _, name = tokens
        name = parser.compile_filter(name)
        return RenderNextNode(name)

    message = "Too %s parameters" % ("many" if len(tokens) > 2 else "few")
    raise TemplateSyntaxError(message)


class RenderRemainderNode(template.Node):
    def __init__(self, name):
        self.name = name

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
        name = parser.compile_filter(name)
        return RenderRemainderNode(name)

    message = "Too %s parameters" % ("many" if len(tokens) > 2 else "few")
    raise TemplateSyntaxError(message)
