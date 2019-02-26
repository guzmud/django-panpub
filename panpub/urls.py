#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf.urls import url 
from django.contrib.auth import views as auth_views

from panpub import views
from panpub import genericviews as gviews
from panpub.models import Platform


p = Platform.load()

if (p and p.use_portal) or (p is None):
    portal_regex = '^$'  # elif not p and not use_portal
else:
    portal_regex = '^op/portal/$'

urlpatterns = [
    url(portal_regex,
        views.portal,
        name='portal',
    ),

    url("^op/configure/$",
        views.platform_configure,
        name='platform_configure',
    ),
    url("^collective/edit/$",
        views.collective_edit,
        name='collective_edit',
    ),
    url("^crafters/register/$",
        views.crafter_register,
        name='crafter_register',
    ),

    url("^collectives/~create/$",
        gviews.CollectiveCreate.as_view(),
        name='collective_create',
    ),
    url("^collectives/(?P<pk>\d+)/~delete/$",
        gviews.CollectiveDelete.as_view(),
        name='collective_delete',
    ),
    url("^collectives/(?P<pk>\d+)/$",
        gviews.CollectiveDetail.as_view(),
        name='collective_detail',
    ),
    url("^collectives/(?P<pk>\d+)/~update/$",
        gviews.CollectiveUpdate.as_view(),
        name='collective_update',
    ),

    url("^crafters/~create/$",
        gviews.CrafterCreate.as_view(),
        name='crafter_create',
    ),
    url("^crafters/(?P<pk>\d+)/~delete/$",
        gviews.CrafterDelete.as_view(),
        name='crafter_delete',
    ),
    url("^crafters/(?P<pk>\d+)/$",
        gviews.CrafterDetail.as_view(),
        name='crafter_detail',
    ),
    url("^crafters/(?P<pk>\d+)/~update/$",
        gviews.CrafterUpdate.as_view(),
        name='crafter_update',
    ),

    url('^works/random/$',
        views.work_random,
        name='work_random',
    ),
    url("^works/(?P<pk>\d+)/$",
        views.work_details,
        name='work_details',
    ),
    url("^works/(?P<pk>\d+)/~delete/$",
        gviews.ContentDelete.as_view(),
        name='work_delete',
    ),
    url("^works/(?P<pk>\d+)/~update/$",
        gviews.ContentUpdate.as_view(),
        name='work_update',
    ),
    url("^works/(?P<pk>\d+)/~mediate/$",
        gviews.ContentMediate.as_view(),
        name='work_mediate',
    ),
    url("^works/(?P<pk>\d+)/export/$",
        views.work_export_form,
        name='work_export_form',
    ),
    url("^works/upload/$",
        views.work_upload,
        name='work_upload',
    ),
    url("^works/corpus/$",
        views.corpus_assemble,
        name='corpus_assemble',
    ),

    url('^op/contact/$',
        views.contact_form,
        name='contact_form',
    ),
    url("^op/export/$",
        views.panpub_export,
        name='panpub_export',
    ),
    url("^op/load-inputtypes/",
        views.load_inputtypes,
        name="load_inputtypes",
    ),
]

if p and p.use_portal:
    urlpatterns += [
        url(r'^profile/$',
            views.profile_edit,
            name='profile_edit',
            ),
        url(r'^login/$',
            auth_views.login,
            {'template_name': 'panpub/accounts/login.html'},
            name='login',
            ),
        url(r'^logout/$',
            auth_views.logout,
            {'next_page': '/'},
            name='logout',
            ),
]
