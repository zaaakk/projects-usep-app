# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView


urlpatterns = patterns('',

    url( r'^info/$',  'browse_app.views.hi', name='info_url' ),

    url( r'^collections/$',  'browse_app.views.collections', name='collections_url' ),

    url( r'^search/$', 'browse_app.search.search_form', name='search_url'),

    url( r'^$',  RedirectView.as_view(pattern_name='info_url') ),

    )
