from django.db import models


class Foobar(models.Model):
    title = models.CharField(max_length=100)


class SubFoobar(Foobar):
    pass
