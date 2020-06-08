Documentation
=============

The documentation files are in ``/docs`` and written with
`Spinx-Doc <https://www.sphinx-doc.org/en/master/>`_ in
`reStructuredText <https://docutils.sourceforge.io/rst.html>`_ language.
`ReStructuredText <https://docutils.sourceforge.io/rst.html>`_ is like Markdown
with some extra features.

The docs can be build as HTML, PDF or E-PUB.

To build HTML files use::

    $ docker-compose -f local.yml run --rm django make --directory docs html

The compiled HTML files are in ``/docs/_build/html``.

When uploading the docs on https://readthedocs.io as a github hook, it will
auto compile each version as HTML, PDF & E-PUB.

The latest version of the docs are on https://mapniktileserver.readthedocs.io/en/latest/?badge=latest
