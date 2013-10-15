armstrong.core.arm_layout
=========================
Provides layout related code for use in Armstrong and Django projects.

``arm_layout`` provides you with tools to help streamline displaying content
from within your application.


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
#. ``pip install armstrong.core.arm_layout``

#. Add ``armstrong.core.arm_layout`` to your ``INSTALLED_APPS``


Contributing
------------

* Create something awesome -- make the code better, add some functionality,
  whatever (this is the hardest part).
* `Fork it`_
* Create a topic branch to house your changes
* Get all of your commits in the new topic branch
* Submit a `pull request`_

.. _pull request: http://help.github.com/pull-requests/
.. _Fork it: http://help.github.com/forking/


State of Project
----------------
Armstrong is an open-source news platform that is freely available to any
organization.  It is the result of a collaboration between the `Texas Tribune`_
and `The Center for Investigative Reporting`_ and a grant from the
`John S. and James L. Knight Foundation`_.

To follow development, be sure to join the `Google Group`_.

``armstrong.core.arm_layout`` is part of the `Armstrong`_ project.  You're
probably looking for that.

.. _Texas Tribune: http://www.texastribune.org/
.. _The Center for Investigative Reporting: http://cironline.org/
.. _John S. and James L. Knight Foundation: http://www.knightfoundation.org/
.. _Google Group: http://groups.google.com/group/armstrongcms
.. _Armstrong: http://www.armstrongcms.org/


License
-------
Copyright 2011-2013 Texas Tribune and The Center for Investigative Reporting

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
