armstrong.core.arm_layout
=========================
Provides layout related code for use in Armstrong and Django projects.

``arm_layout`` provides you with tools to help streamline displaying content
from within your application.


Usage
-----
To load the template tags, add the following line (generally at the top of your
template):

::

    {% load layout_helpers %}

Once you have loaded the ``layout_helpers``, you can use the ``render_model``
template tag to display a given model like this:

::

    {% render_model some_model "full_page" %}

``some_model`` is a variable in your template that is a model instance and the
string ``"full_page"`` is the name of your "layout".  ``render_model`` looks
for a template named ``layouts/<app_label>/<model>/<layout>.html`` to determine
what to use to display your model instance.

``render_model`` goes one step further, however.  It is smart enough to walk
through the inheritance of the model to determine if there are any other models
that have the layout that could be used.  For example, if ``some_model`` was
an instance of ``armstrong.apps.articles.models.Article`` which inherits from
``armstrong.apps.content.models.Content``, ``render_model`` looks in the
following templates:

::

    ["layout/articles/article/full_page.html",
     "layout/content/content/full_page.html", ]

You have access to the entire template context inside the ``full_page.html``
template.  You also have a new variable called ``object`` which represents the
model instance that you provided to ``render_model``.  That variable is only
available inside the layout template and temporarily overrides any context
variable called ``object``.  Once ``render_model`` is finished, it restores the
original context.


Installation & Configuration
----------------------------
You can install the latest release of ``armstrong.core.arm_layout`` using `pip`_:

::

    pip install armstrong.core.arm_layout

Make sure to add ``armstrong.core.arm_layout`` to your ``INSTALLED_APPS``.  You
can add this however you like.  This works as a copy-and-paste solution:

::

	INSTALLED_APPS += ["armstrong.core.arm_layout", ]

.. _pip: http://www.pip-installer.org/


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
Foundation`_.

To follow development, be sure to join the `Google Group`_.

``armstrong.core.arm_layouts`` is part of the `Armstrong`_ project.  You're
probably looking for that.

.. _Texas Tribune: http://www.texastribune.org/
.. _Bay Citizen: http://www.baycitizen.org/
.. _John S. and James L. Knight Foundation: http://www.knightfoundation.org/
.. _Google Group: http://groups.google.com/group/armstrongcms
.. _Armstrong: http://www.armstrongcms.org/


License
-------
Copyright 2011-2012 Bay Citizen and Texas Tribune

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
