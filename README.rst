armstrong.core.arm_layout
=========================
Layout code related to Armstrong

.. warning:: This is development level software.  Please do not unless you are
             familiar with what that means and are comfortable using that type
             of software.


Installation
------------

::

    name="armstrong.core.arm_layout"
    pip install -e git://github.com/armstrong/$name#egg=$name


Usage
-----
First, make sure that ``armstrong.core.arm_layout`` is installed then add it to
the ``INSTALLED_APPS`` list of your Django settings.  Next, inside any
templates you want to use this in, add the following line (generally at the
top of the file)::

    {% load layout_helpers %}

Now, you can use the ``{% render_model %}`` template tag to render any model
like this::

    {% render_model some_model "full_page" %}

Let's assume ``some_model`` is a model called ``Article`` that extends the
model ``Content``.  These models are in ``armstrong.apps.articles`` and
``armstrong.apps.content``, respectively.  This would attempt to load the
following templates in your configured template directories::

    ["layout/articles/article/full_page.html",
     "layout/content/content/full_page.html", ]

These template names follow the pattern of
``layout/<app_label>/<model_name>/<name>.html``.  ``armstrong.core.arm_layout``
is currently concerned with HTML, so the ``html`` extension is the default.  It
may be configurable in future releases.

The two parameters you provide ``render_model`` are a variable that represents
a model and the name of the layout you want to use for that model.  The name
can be either a string (surrounded by single or double quotation marks) or a
variable to that can be resolved to a string.

Inside the various ``full_page.html`` templates, you have access to the entire
context of the calling template, plus a new variable called ``object`` that
represents the model you passed in.

.. note:: The ``object`` variable inside ``full_page.html`` is only available
          inside the template.  Once ``render_model`` has finished, ``object``
          is removed from the context.  Any variable called ``object`` in the
          calling template is left untouched.


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
and `Bay Citizen`_, and a grant from the `John S. and James L. Knight
Foundation`_.  The first release is scheduled for June, 2011.

To follow development, be sure to join the `Google Group`_.

``armstrong.apps.articles`` is part of the `Armstrong`_ project.  You're
probably looking for that.

.. _Texas Tribune: http://www.texastribune.org/
.. _Bay Citizen: http://www.baycitizen.org/
.. _John S. and James L. Knight Foundation: http://www.knightfoundation.org/
.. _Google Group: http://groups.google.com/group/armstrongcms
.. _Armstrong: http://www.armstrongcms.org/


License
-------
Copyright 2011 Bay Citizen and Texas Tribune

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
