# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from django_panpub.urls import urlpatterns as django_panpub_urls

urlpatterns = [
    url(r'^', include(django_panpub_urls, namespace='django_panpub')),
]
