.. _monitoring:

Monitoring
==========

Flower
------

Flower is celery task monitor. Here you can watch, how the tiles are produced and
if there any errors.

To access flower, you need to add the flower username & password in your
``.envs/.production/.django`` for poduction and ``.envs/.local/.django`` for the
development instance.

    # Celery / Flower
    # ------------------------------------------------------------------------------
    CELERY_FLOWER_USER=msshnhBNlGfVLiDTErFKxFWpBOrcZNVp
    CELERY_FLOWER_PASSWORD=eIYplziix19gsYgGfu7HsVzlhHUwFJxQikoOwDlSDnYCjQEjo1atzobXZCyrmnG0

On the development instance, you can access flower over http://localhost:5555
In production, the default URL is https://monitor.ohdm.net
If you want change it to a different domain, modify ``compose/production/traefik/traefik.yml``

Read more at https://flower.readthedocs.io/en/latest/

Sentry.io
---------

`Sentry.io <https://sentry.io>`_ is an online monitoring platform for monitoring
erros. To enable it, add the enviroment var ``SENTRY_DSN`` in ``.envs/.production/.django``
with your account sentry DNS.
