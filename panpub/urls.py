# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(
        regex="^Corpus/~create/$",
        view=views.CorpusCreateView.as_view(),
        name='Corpus_create',
    ),
    url(
        regex="^Corpus/(?P<pk>\d+)/~delete/$",
        view=views.CorpusDeleteView.as_view(),
        name='Corpus_delete',
    ),
    url(
        regex="^Corpus/(?P<pk>\d+)/$",
        view=views.CorpusDetailView.as_view(),
        name='Corpus_detail',
    ),
    url(
        regex="^Corpus/(?P<pk>\d+)/~update/$",
        view=views.CorpusUpdateView.as_view(),
        name='Corpus_update',
    ),
    url(
        regex="^Corpus/$",
        view=views.CorpusListView.as_view(),
        name='Corpus_list',
    ),
    url(
        regex="^Text/~create/$",
        view=views.TextCreateView.as_view(),
        name='Text_create',
    ),
    url(
        regex="^Text/(?P<pk>\d+)/~delete/$",
        view=views.TextDeleteView.as_view(),
        name='Text_delete',
    ),
    url(
        regex="^Text/(?P<pk>\d+)/$",
        view=views.TextDetailView.as_view(),
        name='Text_detail',
    ),
    url(
        regex="^Text/(?P<pk>\d+)/~update/$",
        view=views.TextUpdateView.as_view(),
        name='Text_update',
    ),
    url(
        regex="^Text/$",
        view=views.TextListView.as_view(),
        name='Text_list',
    ),
	]
