# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, json, logging, os, pprint
from . import settings_app
from .models import FlatCollection
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


def collections( request ):
  """Displays list of collections by Region."""
  ## helpers ##
  def prepare_data():
    fc = FlatCollection()
    all_collections_objects = FlatCollection.objects.all().order_by( 'region_name', 'collection_code' )
    all_collections_dictionaries = [ obj.as_dict() for obj in all_collections_objects ]
    data_dict = {
      'region_codes': fc.make_region_codes_list(),
      'all_collections_dictionaries': all_collections_dictionaries,
      'login_url': reverse('admin:index' )  # yes
    }
    return data_dict
  def build_response( format, callback ):
    if format == 'json':
      output = json.dumps( data_dict, sort_keys=True, indent=2 )
      if callback:
        output = '%s(%s)' % ( callback, output )
      return HttpResponse( output, content_type = 'application/javascript; charset=utf-8' )
    else:

      return render( request, 'browse_app_templates/collectionS.html', data_dict )
  ## work ##
  data_dict = prepare_data()
  format = request.GET.get( 'format', None )
  callback = request.GET.get( 'callback', None )
  response = build_response( format, callback )
  return response
