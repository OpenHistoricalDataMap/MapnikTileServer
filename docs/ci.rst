C/I
===

.. index:: CI

About
-----

MapntikTileServer use Github.com Marketplace Apps to maintain the project. Every App is for
free for Open Source projects!

Code Style
----------

.. index:: Code Style

Black
^^^^^

.. index:: Black

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style

`Black <https://github.com/ambv/black>`_ is not integrated as a C/I, it's just a python code auto
formater for the project. So if you like to contribute your code use black by ``python black ./``!

Tests
-----

.. index:: Tests
.. index:: Travis

Travis
^^^^^^

.. image:: https://travis-ci.com/OpenHistoricalDataMap/MapnikTileServer.svg?branch=master
     :target: https://travis-ci.com/OpenHistoricalDataMap/MapnikTileServer
     :alt: Travis CI tests

This project use for testing `unit test <https://docs.pytest.org/en/latest/>`_,
`django commands <https://docs.djangoproject.com/en/3.0/howto/custom-management-commands/>`_ & Docker-Compose builds
`Travis <https://travis-ci.com/>`_

Travis config is ``.travis.yml`` 

Documentation
-------------

.. index:: Documentation

Readthedocs.org
^^^^^^^^^^^^^^^

.. index:: Readthedocs

.. image:: https://readthedocs.org/projects/mapniktileserver/badge/?version=latest
     :target: https://mapniktileserver.readthedocs.io/en/latest/?badge=latest
     :alt: Documentation Status

Documentation is written in `Sphinx <https://www.sphinx-doc.org/en/master/>`_ in ``.rst`` file
format. The sourcecode of the docs is in ``docs/`` 

Travis config is ``.readthedocs.yml``

Code Review
-----------

.. index:: Auto Code Review

Codacy.com
^^^^^^^^^^

.. index:: Codacy

.. image:: https://api.codacy.com/project/badge/Grade/09b0518479d547d2a86c2a925e525160
     :target: https://www.codacy.com/manual/OpenHistoricalDataMap/MapnikTileServer?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=OpenHistoricalDataMap/MapnikTileServer&amp;utm_campaign=Badge_Grade
     :alt: Codacy quality
.. image:: https://api.codacy.com/project/badge/Coverage/09b0518479d547d2a86c2a925e525160
     :target: https://www.codacy.com/manual/OpenHistoricalDataMap/MapnikTileServer?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=OpenHistoricalDataMap/MapnikTileServer&amp;utm_campaign=Badge_Coverage
     :alt: Coverage

`Codacy.com <https://www.codacy.com>`_ is an automated code analysis/quality tool. Codacy analyze
only python for this project, also the coverage of the test are uploaded to
`Codacy.com <https://www.codacy.com>`_ via `Travis <https://travis-ci.com/>`_.

DeepSource.io
^^^^^^^^^^^^^

.. index:: Deepsource

.. image:: https://static.deepsource.io/deepsource-badge-light-mini.svg
     :target: https://deepsource.io/gh/OpenHistoricalDataMap/MapnikTileServer/?ref=repository-badge
     :alt: DeepSource

`DeepSource.io <https://www.deepsource.io>`_ is like `Codacy.com <https://www.codacy.com>`_
but it also analyze Dockerfiles.

DeepSource config is ``.deepsource.toml``

Dependencies
------------

.. index:: Update Dependencies

Pyup.io
^^^^^^^

.. index:: Update Python packages

.. image:: https://pyup.io/repos/github/OpenHistoricalDataMap/MapnikTileServer/shield.svg
     :target: https://pyup.io/repos/github/OpenHistoricalDataMap/MapnikTileServer/
     :alt: Updates

.. image:: https://pyup.io/repos/github/OpenHistoricalDataMap/MapnikTileServer/python-3-shield.svg
     :target: https://pyup.io/repos/github/OpenHistoricalDataMap/MapnikTileServer/
     :alt: Python 3

`Pyup.io <https://pyup.io>`_ update Python packages once a week. It push every update to an extra
banch & create a pull request.

Pyup config is ``.pyup.yml``

Dependabot.com
^^^^^^^^^^^^^^

.. index:: Update Dockerfiles

`Dependabot.com <https://dependabot.com/>`_ update Dockerfiles once a week. It push every update to
an extra banch & create a pull request.

Dependabot config is ``.dependabot/config.yml``