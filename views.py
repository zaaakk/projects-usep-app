# -*- coding: utf-8 -*-

import json, logging, pprint
import requests
from django.conf import settings as settings_project
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.views.decorators.cache import cache_page
from usep_app import settings_app, models
from .models import AboutPage, ContactsPage, LinksPage, PublicationsPage, TextsPage  # static pages
from .models import FlatCollection
from .models import DisplayInscriptionHelper
from usep_app import settings_app


log = logging.getLogger(__name__)
url_map = {"INSCRIPTION":settings_app.TRANSFORMER_XML_URL_SEGMENT,
  "BIB":u"http://library.brown.edu/usep"}


# COMMENT HERE!


## dynamic pages

def get_xml( request ):
    """ Route cross-server requests for xml files through the backend """
    url = u'%s/%s.xml' % (url_map[request.GET["url_key"]], request.GET["inscription_id"])
    r = requests.get( url )
    r.encoding = u'utf-8'
    xml = r.text

    #print "request.META[u'wsgi.url_scheme']: " + str(request.META[u'wsgi.url_scheme'])
    #print "request.get_host(): " + str(request.get_host())

    return HttpResponse( xml.encode(u'utf-8'), content_type=u"text/html; charset=utf-8" )

@cache_page( settings_app.COLLECTIONS_CACHE_SECONDS )
def collections( request ):
  """Displays list of collections by Region."""
  ## helpers ##
  def prepare_data():
    fc = FlatCollection()
    all_collections_objects = FlatCollection.objects.all().order_by( 'region_name', 'collection_code' )
    all_collections_dictionaries = [ obj.as_dict() for obj in all_collections_objects ]
    data_dict = {
      u'region_codes': fc.make_region_codes_list(),
      u'all_collections_dictionaries': all_collections_dictionaries
    }
    return data_dict
  def build_response( format, callback ):
    if format == u'json':
      output = json.dumps( data_dict, sort_keys=True, indent=2 )
      if callback:
        output = u'%s(%s)' % ( callback, output )
      return HttpResponse( output, content_type = u'application/javascript; charset=utf-8' )
    else:
      data_dict[u'login_url'] = settings_app.LOGIN_URL
      return render( request, u'usep_templates/collectionS_dev.html', data_dict )
  ## work ##
  data_dict = prepare_data()
  format = request.GET.get( u'format', None )
  callback = request.GET.get( u'callback', None )
  response = build_response( format, callback )
  return response


def collection( request, collection ):
  """Displays list of inscriptions for given collection."""
  ## helpers ##
  def prepare_data():
    c = models.Collection()
    solr_data = c.get_solr_data( collection )
    inscription_dict = c.enhance_solr_data( solr_data, request.META[u'wsgi.url_scheme'], request.get_host() )
    data_dict = {
      u'collection_title': collection,
      u'inscriptions': inscription_dict,
      u'inscription_count': len( inscription_dict )
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
  data_dict = prepare_data()
  format = request.GET.get( u'format', None )
  callback = request.GET.get( u'callback', None )
  response = build_response( format, callback )
  return response


def display_inscription2( request, inscription_id ):
  """ Displays inscription html from saxon-ce rendering of source xml and an include file of bib data,
      which is then run through an xsl transform. """
  hostname = request.get_host()
  custom_static_url = settings_project.STATIC_URL
  if hostname.lower() == u'usepigraphy.brown.edu':
    custom_static_url = static_url.replace( 'library.brown.edu', 'usepigraphy.brown.edu' )  # so js saxon-ce works as expected
  data_dict = {
    u'url_key': "INSCRIPTION",
    u'inscription_id': inscription_id,
    u'custom_static_url': custom_static_url,
  }
  return render( request, u'usep_templates/inscription2.html', data_dict )


def display_inscription_temp_1( request ):
  """ Displays inscription html from saxon-ce rendering of dummy-source-xml and dummy-include-file,
      which is then run through a dummy-xsl-transform. """
  log.debug( u'display_inscription_temp_1() starting' )
  context = {
    'source_xml_url': settings_app.TEMP_SOURCE_XML_URL,
    'xsl_url': settings_app.TEMP_XSL_URL,
    'saxonce_file_url': settings_app.TEMP_SAXONCE_FILE_URL,
    'xipr_url': settings_app.TEMP_XIPR_URL,
    }
  log.debug( u'display_inscription_temp_1() context, %s' % pprint.pformat(context) )
  return render( request, u'usep_templates/display_inscription_temp_1.html', context )


def display_inscription_temp_2( request ):
  """ Displays inscription html from saxon-ce rendering of hardcoded-real-source-xml and hardcoded-real-include-file,
      which is then run through the hardcoded-real-xsl-transform. """
  log.debug( u'display_inscription_temp_2() starting' )
  hostname = request.get_host()
  custom_static_url = settings_project.STATIC_URL
  if hostname.lower() == u'usepigraphy.brown.edu':
    custom_static_url = static_url.replace( 'library.brown.edu', 'usepigraphy.brown.edu' )  # so js saxon-ce works as expected
  context = {
    u'custom_static_url': custom_static_url,
    u'inscription_id': u'CA.Berk.UC.HMA.G.8-4213',
    u'source_xml_url': settings_app.TEMP2_SOURCE_XML_URL,
    u'xsl_url': settings_app.TEMP2_XSL_URL,
    u'saxonce_file_url': settings_app.TEMP2_SAXONCE_FILE_URL,
    u'xipr_url': settings_app.TEMP2_XIPR_URL
    }
  log.debug( u'display_inscription_temp_2() context, %s' % pprint.pformat(context) )
  return render( request, u'usep_templates/display_inscription_temp_2.html', context )


def display_inscription( request, inscription_id ):
  """ Displays inscription html from saxon-ce rendering of source xml and an include file of bib data,
      which is then run through an xsl transform. """
  log.debug( u'display_inscription() starting' )
  display_inscription_helper = DisplayInscriptionHelper()
  custom_static_url = display_inscription_helper.build_custom_static_url(
    settings_project.STATIC_URL, request.get_host() )
  source_xml_url = display_inscription_helper.build_source_xml_url(
    settings_app.DISPLAY_INSCRIPTION_XML_URL_PATTERN, request.is_secure(), request.get_host(), inscription_id )
  context = display_inscription_helper.build_context(
    custom_static_url, inscription_id, source_xml_url, settings_app.DISPLAY_INSCRIPTION_XSL_URL, settings_app.DISPLAY_INSCRIPTION_SAXONCE_FILE_URL, settings_app.DISPLAY_INSCRIPTION_XIPR_URL )
  log.debug( u'display_inscription() context, %s' % pprint.pformat(context) )
  return render( request, u'usep_templates/display_inscription.html', context )



# class DisplayInscriptionHelper(object):
#   """ Helper for views.display_inscription() """

#   def build_custom_static_url( self, project_static_url, hostname ):
#     """ Updates settings_PROJECT STATIC_URL if needed.
#         Returns url.
#         """
#     custom_static_url = project_static_url
#     if hostname.lower() == u'usepigraphy.brown.edu':
#       custom_static_url = custom_static_url.replace( 'library.brown.edu', 'usepigraphy.brown.edu' )  # so js saxon-ce works as expected
#     return custom_static_url

#   def build_source_xml_url( self, url_pattern, is_secure, hostname, inscription_id ):
#     """ Returns url to inscription xml. """
#     scheme = u'https' if ( is_secure == True ) else u'http'
#     url = url_pattern.replace( u'SCHEME', scheme )
#     url = url.replace( u'HOSTNAME', hostname )
#     url = url.replace( u'INSCRIPTION_ID', inscription_id )
#     return url

#   def build_context( self, custom_static_url, inscription_id, source_xml_url, xsl_url, saxonce_url, xipr_url ):
#     """ Returns context dict. """
#     context = {
#       u'custom_static_url': custom_static_url,
#       u'inscription_id': inscription_id,
#       u'source_xml_url': source_xml_url,
#       u'xsl_url': xsl_url,
#       u'saxonce_file_url': saxonce_url,
#       u'xipr_url': xipr_url
#       }
#     return context



def login( request ):
  from django.contrib import auth
  log.debug( u'login() starting' )
  log.debug( u'request.META is: %s' % request.META )
  forbidden_response = u'You are not authorized to use the admin. If you believe you should be, please contact %s .' % settings_app.PERMITTED_ADMIN_CONTACT
  if u'Shibboleth-eppn' in request.META and request.META[ u'Shibboleth-eppn' ] in settings_app.PERMITTED_ADMINS:
    log.debug( u'shib-eppn found & is a permitted-admin' )
    name = request.META[ u'Shibboleth-eppn' ]
  elif settings_app.SPOOFED_ADMIN in settings_app.PERMITTED_ADMINS:
    log.debug( u'spoofed-admin is a permitted-admin' )
    name = settings_app.SPOOFED_ADMIN
  else:
    log.debug( u'not a legit url access; returning forbidden' )
    return HttpResponseForbidden( forbidden_response )
  try:  # authZ successful
    log.debug( u'trying user-object access' )
    user = auth.models.User.objects.get( username=name )
    user.backend = u'django.contrib.auth.backends.ModelBackend'
    auth.login( request, user )
    log.debug( u'user-object obtained & logged-in' )
    return HttpResponseRedirect( u'../../admin/usep_app/' )
  except Exception, e:  # could auto-add user
    log.debug( u'error: %s' % repr(e).decode(u'utf-8', u'replace') )
    return HttpResponseForbidden( forbidden_response )


def publications( request ):
  # ## build info
  # pubs = models.Publications()
  # pubs.getPubData()  # makes solr call
  # pubs.buildPubLists()
  # data_dict = {
  #   u'master_dict': pubs.master_pub_dict,
  #   u'corpora_list': pubs.corpora,
  #   u'journals_list': pubs.journals,
  #   u'monographs_list': pubs.monographs,
  #   u'url_key': "BIB",
  #   u'inscription_id': 'usepi_bib'
  # }
  # ## store inscription_ids for each publication to session for pubChildren()
  # request.session['publications_to_inscription_ids_dict'] = data_dict['master_dict']
  # ## display
  # format = request.GET.get( u'format', None )
  # callback = request.GET.get( u'callback', None )
  # if format == u'json':
  #   output = json.dumps( data_dict, sort_keys=True, indent=2 )
  #   if callback:
  #     output = u'%s(%s)' % ( callback, output )
  #   return HttpResponse( output, content_type = u'application/javascript; charset=utf-8' )
  # else:
  #   return render( request, u'usep_templates/publications.html', data_dict )

  hostname = request.get_host()
  custom_static_url = settings_project.STATIC_URL
  if hostname.lower() == u"usepigraphy.brown.edu":
    custom_static_url = static_url.replace(u"library.brown.edu", u"usepigraphy.brown.edu")

  data_dict = {
    u'url_key': u"BIB",
    u'inscription_id': u'usepi_bib',
    u'custom_static_url': custom_static_url,
  }
  return render( request, u'usep_templates/publications.html', data_dict )

def pubChildren( request, publication ):
  """displays listing of inscriptions for publication"""
  log.debug( u'publication: %s' % publication )
  assert type( publication ) == unicode

  #print "pubChildren with publication: " + publication

  if not u'publications_to_inscription_ids_dict' in request.session:
    #print "before initializing Publications"
    pubs = models.Publications()
    #print "about make pubs get pub data"
    pubs.getPubData()  # makes solr call
    #print "building the publication result"
    pubs.buildPubLists()
    request.session['publications_to_inscription_ids_dict'] = pubs.master_pub_dict  # key: publication; value: list of inscription_ids

  #print "about to get publication specific data for publication: " + publication
  data = request.session[u'publications_to_inscription_ids_dict'][publication]
  #print "data retrieved: " + str(data)
  log.debug( u'publication data: %s' % data )

  #print "calling the Publication model"
  pub = models.Publication()
  pub.getPubData( data )
  pub.buildInscriptionList( request.META[u'wsgi.url_scheme'], request.get_host() )
  pub.makeImageUrls()
  data_dict = {
    u'publication_title': publication,
    u'inscriptions': pub.inscription_entries,
    u'inscription_count': pub.inscription_count }
  ## respond
  format = request.GET.get( u'format', None )
  callback = request.GET.get( u'callback', None )
  if format == u'json':
    output = json.dumps( data_dict, sort_keys=True, indent=2 )
    if callback:
      output = u'%s(%s)' % ( callback, output )
    return HttpResponse( output, content_type = u'application/javascript; charset=utf-8' )
  else:
    return render( request, u'usep_templates/publicatioN.html', data_dict )


# def pubChildren( request, publication ):
#   """displays listing of inscriptions for publication"""
#   log.debug( u'publication: %s' % publication )
#   assert type( publication ) == unicode
#   if not u'publications_to_inscription_ids_dict' in request.session:
#     pubs = models.Publications()
#     pubs.getPubData()  # makes solr call
#     pubs.buildPubLists()
#     request.session['publications_to_inscription_ids_dict'] = pubs.master_pub_dict  # key: publication; value: list of inscription_ids
#   data = request.session[u'publications_to_inscription_ids_dict'][publication]
#   log.debug( u'publication data: %s' % data )
#   pub = models.Publication()
#   pub.getPubData( data )
#   pub.buildInscriptionList( request.META[u'wsgi.url_scheme'], request.META[u'SERVER_NAME'] )
#   pub.makeImageUrls()
#   data_dict = {
#     u'publication_title': publication,
#     u'inscriptions': pub.inscription_entries,
#     u'inscription_count': pub.inscription_count }
#   ## respond
#   format = request.GET.get( u'format', None )
#   callback = request.GET.get( u'callback', None )
#   if format == u'json':
#     output = json.dumps( data_dict, sort_keys=True, indent=2 )
#     if callback:
#       output = u'%s(%s)' % ( callback, output )
#     return HttpResponse( output, content_type = u'application/javascript; charset=utf-8' )
#   else:
#     return render( request, u'usep_templates/publicatioN.html', data_dict )


## static pages


def about( request ):
  page_data = AboutPage.objects.all()[0]  # just one record
  page_dict = {
    u'page_data': page_data,
    u'settings_app': settings_app }
  return render( request, u'usep_templates/static.html', page_dict )
  # return render_to_response( u'usep_templates/static.html', page_dict )

def texts( request ):
  page_data = TextsPage.objects.all()[0]  # just one record
  page_dict = {
    u'page_data': page_data,
    u'settings_app': settings_app }
  return render( request, u'usep_templates/static.html', page_dict )
  # return render_to_response( u'usep_templates/static.html', page_dict )

def links( request ):
  page_data = LinksPage.objects.all()[0]  # just one record
  page_dict = {
    u'page_data': page_data,
    u'settings_app': settings_app }
  return render( request, u'usep_templates/static.html', page_dict )
  # return render_to_response( u'usep_templates/static.html', page_dict )

def contact( request ):
  page_data = ContactsPage.objects.all()[0]  # just one record
  page_dict = {
    u'page_data': page_data,
    u'settings_app': settings_app }
  return render( request, u'usep_templates/static.html', page_dict )
  # return render_to_response( u'usep_templates/static.html', page_dict )

def temp( request ):
  return HttpResponse( u'<p>under construction</p>')
