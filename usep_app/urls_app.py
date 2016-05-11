# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView


urlpatterns = patterns('',

    url( r'^info/$',  'usep_app.views.hi', name='info_url' ),

    url( r'^collections/$',  'usep_app.views.collections', name='collections_url' ),

    url( r'^search/$', 'usep_app.search.search_form', name='search_url'),

    url( r'^$',  RedirectView.as_view(pattern_name='collections_url') ),

    )
