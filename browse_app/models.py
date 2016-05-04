# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.encoding import smart_unicode


log = logging.getLogger(__name__)


class FlatCollection( models.Model ):
    """ Represents non-hierarchical collection.
        (django-db collection class) """
    collection_code = models.CharField( blank=True, max_length=50 )
    region_code = models.CharField( blank=True, max_length=10 )
    region_name = models.CharField( blank=True, max_length=50 )
    settlement_code = models.CharField( blank=True, max_length=10 )
    institution_code = models.CharField( blank=True, max_length=10 )
    repository_code = models.CharField( blank=True, max_length=10 )
    collection_name = models.CharField( blank=True, max_length=100 )
    collection_address = models.CharField( blank=True, max_length=200, help_text=u'single string' )
    collection_url = models.CharField( blank=True, max_length=200 )
    collection_description = models.TextField( blank=True )

    def __unicode__(self):
        return smart_unicode( self.collection_code, u'utf-8', u'replace' )

    def save(self):
        """ Auto-builds collection_code from component parts if they exist. """
        if len( self.collection_code.strip() ) == 0:
            new_collection_code = self.region_code.strip()
            if len( self.settlement_code.strip() ) > 0:
                new_collection_code = u'%s.%s' % ( new_collection_code, self.settlement_code.strip() )
            if len( self.institution_code.strip() ) > 0:
                new_collection_code = u'%s.%s' % ( new_collection_code, self.institution_code.strip() )
            if len( self.repository_code.strip() ) > 0:
                new_collection_code = u'%s.%s' % ( new_collection_code, self.repository_code.strip() )
            self.collection_code = new_collection_code
        super(FlatCollection, self).save() # Call the "real" save() method

    def as_dict(self):
        """ Allows easy serializing to json of queryset. """
        return {
            u'collection_code': self.collection_code,
            u'region_code': self.region_code,
            u'region_name': self.region_name,
            u'settlement_code': self.settlement_code,
            u'institution_code': self.institution_code,
            u'repository_code': self.repository_code,
            u'collection_name': self.collection_name,
            u'collection_address': self.collection_address,
            u'collection_url': self.collection_url,
            u'collection_description': self.collection_description,
        }

    def make_region_codes_list(self):
        """ Returns unique sorted list of region codes. """
        from browse_app.models import FlatCollection
        q = FlatCollection.objects.values('region_code').distinct()  # type: <class 'django.db.models.query.ValuesQuerySet'>; eg: [{'region_code': u'CA'}, {'region_code': u'MA'}]
        region_codes = []
        for entry in q:
            region_codes.append( entry.values()[0] )
        return sorted( region_codes )

    # end class FlatCollection
