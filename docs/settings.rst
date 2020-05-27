.. _settings:

Settings
========

This project relies extensively on environment settings which **will not work with Apache/mod_wsgi setups**. It has been deployed successfully with both Gunicorn/Nginx and even uWSGI/Nginx.

For configuration purposes, the following table maps environment variables to their Django setting and project settings:


======================================= =========================== ============================================== ======================================================================
Environment Variable                    Django Setting              Development Default                            Production Default
======================================= =========================== ============================================== ======================================================================
DJANGO_READ_DOT_ENV_FILE                READ_DOT_ENV_FILE           False                                          False
======================================= =========================== ============================================== ======================================================================


======================================= =========================== ============================================== ======================================================================
Environment Variable                    Django Setting              Development Default                            Production Default
======================================= =========================== ============================================== ======================================================================
DATABASE_URL                            DATABASES                   auto w/ Docker; postgres://project_slug w/o    raises error
DJANGO_DEBUG                            DEBUG                       True                                           False
DJANGO_SETTINGS_MODULE                  DJANGO_SETTINGS_MODULE      config.settings.local                          raises error -> config.settings.production
DJANGO_SECRET_KEY                       SECRET_KEY                  auto-generated                                 raises error
DJANGO_SECURE_BROWSER_XSS_FILTER        SECURE_BROWSER_XSS_FILTER   n/a                                            True
DJANGO_SECURE_SSL_REDIRECT              SECURE_SSL_REDIRECT         n/a                                            True
DJANGO_SECURE_CONTENT_TYPE_NOSNIFF      SECURE_CONTENT_TYPE_NOSNIFF n/a                                            True
DJANGO_SECURE_FRAME_DENY                SECURE_FRAME_DENY           n/a                                            True
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS   HSTS_INCLUDE_SUBDOMAINS     n/a                                            True
DJANGO_SESSION_COOKIE_HTTPONLY          SESSION_COOKIE_HTTPONLY     n/a                                            True
DJANGO_SESSION_COOKIE_SECURE            SESSION_COOKIE_SECURE       n/a                                            False
DJANGO_DEFAULT_FROM_EMAIL               DEFAULT_FROM_EMAIL          n/a                                            "OHDM Django Mapnik <noreply@ohdm.net>"
DJANGO_SERVER_EMAIL                     SERVER_EMAIL                n/a                                            "OHDM Django Mapnik <noreply@ohdm.net>"
DJANGO_EMAIL_SUBJECT_PREFIX             EMAIL_SUBJECT_PREFIX        n/a                                            "[OHDM Django Mapnik]"
DJANGO_ALLOWED_HOSTS                    ALLOWED_HOSTS               ['*']                                          [a.ohdm.net,b.ohdm.net,c.ohdm.net]
CELERY_BROKER_URL                       CELERY_BROKER_URL           auto w/ Docker; raises error w/o               raises error
SENTRY_DSN                              SENTRY_DSN                  n/a                                            False
DJANGO_SENTRY_LOG_LEVEL                 SENTRY_LOG_LEVEL            n/a                                            logging.INFO
CARTO_STYLE_PATH                        CARTO_STYLE_PATH            /opt/openstreetmap-carto                       raises error
CARTO_STYLE_PATH_DEBUG                  CARTO_STYLE_PATH_DEBUG      /opt/openstreetmap-carto-debug                 n/a
TILE_GENERATOR_SOFT_TIMEOUT             TILE_GENERATOR_SOFT_TIMEOUT 240                                            240
TILE_GENERATOR_HARD_TIMEOUT             TILE_GENERATOR_HARD_TIMEOUT 360                                            360
CACHE_VIEW                              CACHE_VIEW                  86400                                          86400
ZOOM_LEVEL                              ZOOM_LEVEL                  13                                             13
TILE_CACHE_TIME                         TILE_CACHE_TIME             2592000                                        2592000
======================================= =========================== ============================================== ======================================================================
