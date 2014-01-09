from django.db import models


class Foobar(models.Model):
    title = models.CharField(max_length=100)


class SubFoobar(Foobar):
    pass


class HasOwnLayoutMethod(models.Model):
    def get_layout_template_name(self, name):
        return ["my_layouts/%s/%s.file" % (type(self).__name__.lower(), name)]
