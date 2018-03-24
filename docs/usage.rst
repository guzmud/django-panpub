=====
Usage
=====

To use Django Panpub in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_panpub.apps.DjangoPanpubConfig',
        ...
    )

Add Django Panpub's URL patterns:

.. code-block:: python

    from django_panpub import urls as django_panpub_urls


    urlpatterns = [
        ...
        url(r'^', include(django_panpub_urls)),
        ...
    ]
