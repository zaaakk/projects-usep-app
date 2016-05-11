# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView


urlpatterns = patterns('',

    url( r'^info/$',  'usep_app.views.hi', name='info_url' ),

    # url( r'^search/$', 'usep_app.search.search_form', name='search_url'),
    url( r'^search/$', 'usep_app.views.coming', name='search_url'),
    url( r'^collections/$',  'usep_app.views.collections', name='collections_url' ),
    url( r'^publications/$',  'usep_app.views.coming', name='publications_url' ),

    url( r'^texts/$',  'usep_app.views.coming', name='texts_url' ),
    url( r'^links/$',  'usep_app.views.coming', name='links_url' ),
    url( r'^about/$',  'usep_app.views.coming', name='about_url' ),
    url( r'^contact/$',  'usep_app.views.coming', name='contact_url' ),

    url( r'^collections/(?P<collection>[^/]+)/$',  'usep_app.views.collection', name='collection_url' ),

    url( r'^$',  RedirectView.as_view(pattern_name='collections_url') ),

    )
