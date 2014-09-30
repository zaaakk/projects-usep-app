# -*- coding: utf-8 -*-

# from django.conf.urls.defaults import *
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
from usep_app import settings_app


urlpatterns = patterns('',

  ## static pages

  url( r'^about/$',  'usep_app.views.about', name='about_url' ),
  url( r'^texts/$',  'usep_app.views.texts', name='texts_url' ),
  url( r'^links/$',  'usep_app.views.links', name='links_url' ),
  url( r'^contact/$',  'usep_app.views.contact', name='contact_url' ),

  ## dynamic pages

  url( r'^collections/$',  'usep_app.views.collections', name='collections_url' ),
  url( r'^collections/(?P<collection>[^/]+)/$',  'usep_app.views.collection', name='collection_url' ),

  url( r'^inscription/(?P<inscription_id>[^/]+)/$', 'usep_app.views.display_inscription', name='inscription_url' ),

  url( r'^getxml/$',  'usep_app.views.get_xml', name='get_xml_url' ),

  url( r'^login/$',  'usep_app.views.login', name='login_url' ),

  url( r'^publications/$',  'usep_app.views.publications', name='publications_url' ),
  url( r'^publication/(?P<publication>[^/]+)/$', 'usep_app.views.pubChildren', name='publication_url' ),

  ( r'^$', redirect_to, {'url': '/%s/collections/' % settings_app.PROJECT_APP} ),

  )
