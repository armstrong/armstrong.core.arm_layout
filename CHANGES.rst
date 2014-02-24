CHANGES
=======

1.3.0 (2014-02-24)
------------------

- **DEPRECATION:** ``BasicRenderModelBackend`` is now ``BasicLayoutBackend``
  The new name better reflects the Armstrong component and its purpose.
  The "render_model" name is more of a template tag implementation detail.

- **DEPRECATION:** ``ARMSTRONG_RENDER_MODEL_BACKEND`` is now
  ``ARMSTRONG_LAYOUT_BACKEND``. The new setting better indicates which
  Armstrong component it belongs to.

- New ``ModelProvidedLayoutBackend`` that allows models to specify their own
  template lookup by implementing ``get_layout_template_name()``.

- Provide model mixins for use with the new backend that handle common
  scenarios such as template lookup using the model's slug, full_slug or type.

- ``render_model`` template tag now accepts ``with`` and ``only`` arguments,
  which work exactly as they do in Django's own include_ template tag.

- Refactored three template tags using Django's simple_tag_ decorator.

- Vast test refactor.


.. _include: https://docs.djangoproject.com/en/1.6/ref/templates/builtins/#include
.. _simple_tag: https://docs.djangoproject.com/en/1.6/howto/custom-template-tags/#django.template.Library.simple_tag
