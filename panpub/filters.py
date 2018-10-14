#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import django_filters

from panpub.models import Crafter, Corpus, Content, Text


class CrafterFilter(django_filters.FilterSet):
    class Meta:
        model = Crafter
        fields = ['user', ]


class CorpusFilter(django_filters.FilterSet):
    class Meta:
        model = Corpus
        fields = ['name', 'license', 'datestamp']


class ContentFilter(django_filters.FilterSet):
    class Meta:
        models = Content
        fields = ['name', 'license', 'datestamp',
                  'claims', 'corpuses']


class TextFilter(django_filters.FilterSet):
    class Meta:
        models = Text
        fields = ['name', 'license', 'datestamp',
                  'claims', 'corpuses']
