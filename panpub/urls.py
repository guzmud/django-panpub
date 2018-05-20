# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(
        regex="^corpus/~create/$",
        view=views.CorpusCreate.as_view(),
        name='Corpus_create',
    ),
    url(
        regex="^corpus/(?P<pk>\d+)/~delete/$",
        view=views.CorpusDelete.as_view(),
        name='Corpus_delete',
    ),
    url(
        regex="^corpus/(?P<pk>\d+)/$",
        view=views.CorpusDetail.as_view(),
        name='Corpus_detail',
    ),
    url(
        regex="^corpus/(?P<pk>\d+)/~update/$",
        view=views.CorpusUpdate.as_view(),
        name='Corpus_update',
    ),
    url(
        regex="^corpus/$",
        view=views.CorpusList.as_view(),
        name='Corpus_list',
    ),
    url(
        regex="^Text/~create/$",
        view=views.TextCreate.as_view(),
        name='Text_create',
    ),
    url(
        regex="^Text/(?P<pk>\d+)/~delete/$",
        view=views.TextDelete.as_view(),
        name='Text_delete',
    ),
    url(
        regex="^Text/(?P<pk>\d+)/$",
        view=views.TextDetail.as_view(),
        name='Text_detail',
    ),
    url(
        regex="^Text/(?P<pk>\d+)/~update/$",
        view=views.TextUpdate.as_view(),
        name='Text_update',
    ),
    url(
        regex="^Text/$",
        view=views.TextList.as_view(),
        name='Text_list',
    ),
	]
