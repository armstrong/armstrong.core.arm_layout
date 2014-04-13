armstrong.core.arm_layout
=========================

.. image:: https://travis-ci.org/armstrong/armstrong.core.arm_layout.svg?branch=master
  :target: https://travis-ci.org/armstrong/armstrong.core.arm_layout
  :alt: TravisCI status
.. image:: https://pypip.in/version/armstrong.core.arm_layout/badge.png
  :target: https://pypi.python.org/pypi/armstrong.core.arm_layout/
  :alt: PyPI Version
.. image:: https://pypip.in/license/armstrong.core.arm_layout/badge.png
  :target: https://pypi.python.org/pypi/armstrong.core.arm_layout/
  :alt: License

Provides layout and templating features for use in Armstrong and Django
projects. ``arm_layout`` provides tools to help streamline displaying content
and excels at rendering standardized, model-specific templates that are easy
to share or overwrite to be as general or specific as you need. Render your
model objects wherever you need them in your templates without worrying about
object specifics or view logic.


Usage
-----
Cheat sheet
"""""""""""
::

    {% load layout_helpers %}

    {% render_model model_obj "template_name" %}

    <!-- otherwise render_model behaves exactly like {% include ... %} -->
    {% render_model model_obj "template_name" with additional="data" %}
    {% render_model model_obj "template_name" with isolated="context" only %}

    <!-- shortcut to call render_model on a list of model objects -->
    {% render_list list_of_models "template_name" %}

    <!-- or more flexible looping -->
    {% render_iter list_of_models %}
        {% render_next "big" %}
        {% render_next "small" %}
        {% render_next "big" %}
        {% render_remainder "small" %}
    {% endrender_iter %}

In depth
""""""""
To load the template tags, add the following line (generally at the top of your
template)::

    {% load layout_helpers %}

Now you can use the ``render_model`` template tag to display a given model
like this::

    {% render_model some_model "full_page" %}

``some_model`` is a variable in your template that is a model instance and the
string ``"full_page"`` is the name of your "layout". ``render_model`` looks
for a template named ``layout/<app_label>/<model>/<layout>.html`` to determine
what to use to display your model instance. Going one step further, it is smart
enough to walk through the inheritance of the model to determine if there are
any parent models that have the layout that can be used. For example, if
``some_model`` was an instance of ``armstrong.apps.articles.models.Article``
that inherits from ``armstrong.apps.content.models.Content``, ``render_model``
looks for the following templates, in this order::

    ["layout/articles/article/full_page.html",
     "layout/content/content/full_page.html", ]

You have access to the entire template context inside the ``full_page.html``
template. You also have a new variable called ``object`` which represents the
model instance that you provided to ``render_model``. That variable is only
available inside the layout template and temporarily overrides any other
context variable called ``object``. Aside from the flexibility of looking up a
template based on model inheritance, this tag works just like `{% include %}`_.
You can add to the context using ``with extra="param"`` or isolate the context
using ``only``. Once ``render_model`` is finished, it restores the original
context.

``layout_helpers`` provides two other helper methods for easily rendering
multiple models without having to manually loop through them. You can render
an entire list of models using the same template::

    {% render_list list_of_models "preview" %}

Or have finer control with a block tag that lets you step through each model
instance specifying the template each time and then rendering all the rest
with a common template::

    {% render_iter list_of_models %}
        {% render_next "preview" %}
        {% render_next "preview" %}
        {% render_next "preview" %}
        {% render_remainder "headline" %}
    {% endrender_iter %}

Of course you could do the same thing another way::

    {% render_list list_of_models[:3] "preview" %}
    {% render_list list_of_models[3:] "headline" %}

A limitation of these loop helpers is they cannot add or limit the context
using ``with`` or ``only`` as ``render_model`` can. You could however wrap
the tags in a ``{% with need="this" and="that" %} ... {% endwith %}`` block.
See the `with documentation`_.

.. _{% include %}: https://docs.djangoproject.com/en/1.5/ref/templates/builtins/#include
.. _with documentation: https://docs.djangoproject.com/en/1.5/ref/templates/builtins/#with


Installation & Configuration
----------------------------
Supports Django 1.3, 1.4, 1.5, 1.6 on Python 2.6 and 2.7.

#. ``pip install armstrong.core.arm_layout``

#. Add ``armstrong.core.arm_layout`` to your ``INSTALLED_APPS``

**Optional Setting:** (Used in ``settings.py`` and safe to omit)

``ARMSTRONG_LAYOUT_BACKEND = "armstrong.core.arm_layout.backends.BasicLayoutBackend"``
  Backends specify how the template tags actually determine template paths.
  There are two options--``BasicLayoutBackend`` and
  ``ModelProvidedLayoutBackend``. Basic uses model inheritance as a directory
  structure. ModelProvided does the same, but optionally allows a model to
  determine its own template lookup. A few model mixins are provided for
  common scenarios. Feel free to write your own backend if you need other
  functionality.


Contributing
------------
Development occurs on Github. Participation is welcome!

* Found a bug? File it on `Github Issues`_. Include as much detail as you
  can and make sure to list the specific component since we use a centralized,
  project-wide issue tracker.
* Testing? ``pip install tox`` and run ``tox``
* Have code to submit? Fork the repo, consolidate your changes on a topic
  branch and create a `pull request`_. The `armstrong.dev`_ package provides
  tools for testing, coverage and South migration as well as making it very
  easy to run a full Django environment with this component's settings.
* Questions, need help, discussion? Use our `Google Group`_ mailing list.

.. _Github Issues: https://github.com/armstrong/armstrong/issues
.. _pull request: http://help.github.com/pull-requests/
.. _armstrong.dev: https://github.com/armstrong/armstrong.dev
.. _Google Group: http://groups.google.com/group/armstrongcms


State of Project
----------------
`Armstrong`_ is an open-source news platform that is freely available to any
organization. It is the result of a collaboration between the `Texas Tribune`_
and `The Center for Investigative Reporting`_ and a grant from the
`John S. and James L. Knight Foundation`_. Armstrong is available as a
complete bundle and as individual, stand-alone components.

.. _Armstrong: http://www.armstrongcms.org/
.. _Texas Tribune: http://www.texastribune.org/
.. _The Center for Investigative Reporting: http://cironline.org/
.. _John S. and James L. Knight Foundation: http://www.knightfoundation.org/
