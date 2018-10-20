#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import django_filters

from panpub.models import Crafter, Corpus, Content, Text


class CrafterFilter(django_filters.FilterSet):
    class Meta:
        model = Crafter
        fields = ['user__username',
                  'user__date_joined',
                  'user__last_login',
                  ]


class CorpusFilter(django_filters.FilterSet):
    class Meta:
        model = Corpus
        fields = ['name',
                  'license',
                  'datestamp',
                  ]


class ContentFilter(django_filters.FilterSet):
    class Meta:
        model = Content
        fields = ['name',
                  'license',
                  'datestamp',
                  'claims__claim__crafter__user__username',
                  'claims__claim__claim_type',
                  'corpuses__name',
                  ]


class TextFilter(django_filters.FilterSet):
    class Meta:
        model = Text
        fields = ['name',
                  'license',
                  'datestamp',
                  'claims__claim__crafter__user__username',
                  'claims__claim__claim_type',
                  'corpuses__name',
                  ]
