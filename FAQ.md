I get "found namespace .pth file".  What should I do?
-----------------------------------------------------

The essential problem with Python namespace packages is that they require
overlapping `__init__.py` files, which are shared by different projects.

The most straightforward way to handle namespace packages in conda is
to create a package which defines the namespace , which only contains a
single empty `__init__.py` file, and then make the other packages depend
on this.
This is how we handle namespace packages in the Anaconda distribution.
For example, the
<a href="https://github.com/ContinuumIO/anaconda-recipes/tree/master/backports">
backports recipe</a>defines the `backports` namespace, and then other
packages, such as
<a href="https://github.com/ContinuumIO/anaconda-recipes/tree/master/configparser">
configparser</a>depend on `backports`.

There are other ways to get around this problem, e.g. by preserving the egg
directory which setuptools creates, but that is not as simple and
clean (from a packaging perspective), and brings along other challenges.
