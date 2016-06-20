# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, json, logging, os, pprint
from . import models, settings_app
from .models import AboutPage, ContactsPage, LinksPage, PublicationsPage, TextsPage  # static pages
from .models import DisplayInscriptionHelper, FlatCollection
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

log = logging.getLogger(__name__)


def hi( request ):
    """ Returns simplest response. """
    now = datetime.datetime.now()
    return HttpResponse( '<p>hi</p> <p>( %s )</p>' % now )


def coming( request ):
    """ Stub view. """
    return HttpResponse( '<p>coming</p>')


def collections( request ):
  """Displays list of collections by Region."""
  log.debug( 'starting collections()' )
  ## helpers ##
  def prepare_data():
    fc = FlatCollection()
    all_collections_objects = FlatCollection.objects.all().order_by( 'region_name', 'collection_code' )
    all_collections_dictionaries = [ obj.as_dict() for obj in all_collections_objects ]
    data_dict = {
      'region_codes': fc.make_region_codes_list(),
      'all_collections_dictionaries': all_collections_dictionaries,
      'login_url': reverse('admin:usep_app_flatcollection_changelist' ),
      'search_url': reverse( 'search_url' ), 'collections_url': reverse( 'search_url' ), 'publications_url': reverse( 'publications_url' ),
      'texts_url': reverse( 'texts_url' ), 'links_url': reverse( 'links_url' ), 'about_url': reverse( 'about_url' ), 'contact_url': reverse( 'contact_url' ),
    }
    return data_dict
  def build_response( format, callback ):
    if format == 'json':
      output = json.dumps( data_dict, sort_keys=True, indent=2 )
      if callback:
        output = '%s(%s)' % ( callback, output )
      return HttpResponse( output, content_type = 'application/javascript; charset=utf-8' )
    else:

      return render( request, 'usep_templates/collectionS.html', data_dict )
  ## work ##
  data_dict = prepare_data()
  format = request.GET.get( 'format', None )
  callback = request.GET.get( 'callback', None )
  response = build_response( format, callback )
  return response




def collection( request, collection ):
    """Displays list of inscriptions for given collection."""
    ## helpers ##
    def prepare_data():
        c = models.Collection()
        solr_data = c.get_solr_data( collection )
        inscription_dict, num, display_dict = c.enhance_solr_data( solr_data, request.META[u'wsgi.url_scheme'], request.get_host() )
        data_dict = {
            u'collection_title': collection,
            u'inscriptions': inscription_dict,
            u'inscription_count': num,
            u'display': display_dict,
            u'flat_collection': FlatCollection.objects.get(collection_code=collection),
            u'show_dates':False,
            }
        return data_dict
    def build_response( format, callback ):
        if format == u'json':
            output = json.dumps( data_dict, sort_keys=True, indent=2 )
            if callback:
                output = u'%s(%s)' % ( callback, output )
            return HttpResponse( output, content_type = u'application/javascript; charset=utf-8' )
        else:
            return render( request, u'usep_templates/collectioN.html', data_dict )
    ## work ##
    log.debug( 'starting collection()' )
    data_dict = prepare_data()
    format = request.GET.get( u'format', None )
    callback = request.GET.get( u'callback', None )
    response = build_response( format, callback )
    return response




def display_inscription( request, inscription_id ):
    """ Displays inscription html from saxon-ce rendering of source xml and an include file of bib data,
      which is then run through an xsl transform. """
    log.debug( u'display_inscription() starting' )
    display_inscription_helper = DisplayInscriptionHelper()  # models.py
    source_xml_url = display_inscription_helper.build_source_xml_url(
        settings_app.DISPLAY_INSCRIPTION_XML_URL_PATTERN, request.is_secure(), request.get_host(), inscription_id )
    context = display_inscription_helper.build_context(
        request.get_host(),
        project_settings.STATIC_URL,
        inscription_id,
        source_xml_url,
        settings_app.DISPLAY_INSCRIPTION_XSL_URL,
        settings_app.DISPLAY_INSCRIPTION_SAXONCE_FILE_URL,
        settings_app.DISPLAY_INSCRIPTION_XIPR_URL )
    log.debug( u'display_inscription() context, %s' % pprint.pformat(context) )
    return render( request, u'usep_templates/display_inscription.html', context )




def publication( request, publication ):
    """ Stub view. """
    return HttpResponse( '<p>coming</p>')


def publications( request ):
    """ Displays list of Corpora, Journals, Monographs, and Unpublished/Missing citations. """
    hostname = request.get_host()
    custom_static_url = project_settings.STATIC_URL
    publications_stylesheet_url = settings_app.DISPLAY_PUBLICATIONS_XSL_URL
    publications_xml_url = settings_app.DISPLAY_PUBLICATIONS_BIB_URL
    if hostname.lower() == u"usepigraphy.brown.edu":
        custom_static_url = custom_static_url.replace(u"library.brown.edu", u"usepigraphy.brown.edu")
        publications_stylesheet_url = publications_stylesheet_url.replace(u"library.brown.edu", u"usepigraphy.brown.edu")
        publications_xml_url = publications_xml_url.replace(u"library.brown.edu", u"usepigraphy.brown.edu")
    data_dict = {
        u'publications_stylesheet_url': publications_stylesheet_url,
        u'publications_xml_url': publications_xml_url,
        u'custom_static_url': custom_static_url,
    }
    return render( request, u'usep_templates/publications.html', data_dict )


## static pages  ##


def texts( request ):
    page_data = TextsPage.objects.all()
    page_data = page_data[0] if page_data else []  # just one record
    page_dct = {
        'page_data': page_data,
        'settings_app': settings_app }
    return render( request, u'usep_templates/static.html', page_dct )

def links( request ):
  page_data = LinksPage.objects.all()[0]  # just one record
  page_dct = {
    u'page_data': page_data,
    u'settings_app': settings_app }
  return render( request, u'usep_templates/static.html', page_dct )
  # return render_to_response( u'usep_templates/static.html', page_dct )

def about( request ):
  page_data = AboutPage.objects.all()[0]  # just one record
  page_dct = {
    u'page_data': page_data,
    u'settings_app': settings_app }
  return render( request, u'usep_templates/static.html', page_dct )
  # return render_to_response( u'usep_templates/static.html', page_dct )

def contact( request ):
  page_data = ContactsPage.objects.all()[0]  # just one record
  page_dct = {
    u'page_data': page_data,
    u'settings_app': settings_app }
  return render( request, u'usep_templates/static.html', page_dct )
  # return render_to_response( u'usep_templates/static.html', page_dct )
