# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, json, logging, os, pprint
from django.conf import settings as project_settings
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.encoding import smart_unicode
from browse_app import settings_app


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


class SolrHelper(object):
    default_params = {
        u'start': u'0',
        u'indent': u'on',
        u'facet': u'on',
        u'facet.mincount': u'1',
        u'facet.limit':u'-1',
        u'wt': u'json' }
    solr_url = settings_app.SOLR_URL_BASE

    default_facets = ["condition", "language", "material",
        "object_type", "text_genre", "writing", "status", "char", "name", "fake"]

    null_fields = ["condition", "material","writing","char","name","fake"]

    def __init__(self):
        self.vocab = Vocab()

    def makeSolrQuery(self, q_obj):
        fields = []
        if u"notBefore" not in q_obj or u"notAfter" not in q_obj:
            # if we have an incomplete date, just skip it
            if u"date_type" in q_obj:
                del q_obj[u"date_type"]
            if u"notBefore" in q_obj:
                del q_obj[u"notBefore"]

            if u"notAfter" in q_obj:
                del q_obj[u"notAfter"]

        elif len(q_obj[u"notBefore"][0]) == 0 or len(q_obj[u"notBefore"][0]) == 0:
            if u"date_type" in q_obj:
                del q_obj[u"date_type"]
            if u"notBefore" in q_obj:
                del q_obj[u"notBefore"]
            if u"notAfter" in q_obj:
                del q_obj[u"notAfter"]

        else:
            dtype = q_obj[u"date_type"][0]
            nb = int(q_obj[u"notBefore"][0])
            na = int(q_obj[u"notAfter"][0])
            del q_obj[u"date_type"]
            del q_obj[u"notBefore"]
            del q_obj[u"notAfter"]
            qstring = u""
            if dtype == u"inclusive":
                qstring = u"(notBefore:[{0} TO {1}] OR notAfter:[{0} TO {1}] OR (notBefore:[* TO {0}] AND notAfter[{1} TO *]) OR (notBefore:[{0} TO *] AND notAfter[* TO {1}]))"
            else:
                qstring = u"(notBefore:[{0} TO *] AND notAfter[* TO {1}])"


            fields += [qstring.format(nb, na)]


        for f in q_obj:
            if f.startswith(u"facet_"):

                if f == u"facet_fake":
                    if q_obj[f][0] == u'not_fake':
                        fields += [u"NOT (fake:*)"]
                    else:
                        fields += ["(fake:*)"]
                    continue

                if q_obj[f][0] == u'none_value':
                    fields += [u"NOT ({0}:*)".format(f[6:])]
                    continue

                fields += [u"({0}:{1})".format(f[6:], q_obj[f][0])]
                continue

            if f == u"fake":
                if q_obj[f][0] == u'hide':
                    fields = fields + [u"NOT (fake:*)"]
                continue

            if f == u"status":
                if q_obj[f][0] == u"transcription":
                    fields = fields + [u"(status:transcription)"]
                elif q_obj[f][0] == u"metadata":
                    fields = fields + [u"(status:transcription OR status:metadata)"]
                else:
                     fields = fields + [u"(status:*)"]
                continue

            values = []
            for v in q_obj[f]:
                if v:
                    values = values + [u"{0}:{1}".format(f,v)]

            if values: fields = fields + [u"("+(u" OR ".join(values))+u")"]

        return u" AND ".join(fields)

    def add_collection(self, result_list):
        for doc in result_list:
            col_list = []
            if u"msid_region" in doc: col_list.append(doc[u'msid_region'])
            if u"msid_settlement" in doc: col_list.append(doc[u'msid_settlement'])
            if u"msid_institution" in doc: col_list.append(doc[u'msid_institution'])
            if u"msid_repository" in doc: col_list.append(doc[u'msid_repository'])

            doc[u'collection'] = u'.'.join(col_list)

        return result_list

    def query(self, q_obj, params={}, search_form=False):
        q = self.makeSolrQuery(q_obj)
        params = dict(params.items() + self.default_params.items())
        params[u'facet.mincount'] = "1"
        params[u'facet.field'] = self.default_facets
        params[u'facet.query'] = ["NOT {0}:*".format(f) for f in self.null_fields]
        params[u'q'] = q

        r = requests.get(self.solr_url, params=params)
        resp = r.json
        if "error" in resp:
            return resp, None, None
        return self.add_collection(resp['response']['docs']), self.facetDisplay(resp['facet_counts'], search_form), q

    def facetDisplay(self, facets, form=False):
        """Make a display dict from a solr facet result, parsing the counts into a dict"""
        facet_displays = dict()
        facet_dict = facets['facet_fields']
        facet_queries = facets['facet_queries']

        def name_key(value):
            if "." in value[0]:
                return (self.vocab[value[0].split(".")[0]].lower(), self.vocab[value[0]].lower())
            else:
                return (self.vocab[value[0]].lower(), value[0].lower())

        sorter = lambda x: -x[1]
        if form:
            sorter = name_key

        for field in facet_dict:
            facet_displays[field] = dict()
            counts = facet_dict[field]
            if field == u"fake":
                num = sum([counts[x] for x in range(1, len(counts), 2)])
                li = []
                if num != 0: li += [("fake",num)]
                if facet_queries["NOT fake:*"] != 0: li += [("not_fake",facet_queries["NOT fake:*"])]
                facet_displays[u"fake"] = li

                continue

            total = 0

            for i in range(0,len(counts), 2):
                f_display = counts[i]
                facet_displays[field][f_display] = counts[i+1]
                total += counts[i+1]

            if "NOT {0}:*".format(field) in facet_queries:
                facet_displays[field]["none_value"] = facet_queries["NOT {0}:*".format(field)]
            facet_displays[field] = sorted(facet_displays[field].items(), key=sorter)

        return facet_displays

    def enhance_solr_data( self, solr_data, url_scheme, server_name ):
        """ Adds to dict entries from solr: image-url and item-url. """
        enhanced_list = []
        for entry in solr_data:
            image_url = None
            if u'graphic_name' in entry.keys():
                image_url = u'%s/%s' % ( settings_app.INSCRIPTIONS_URL_SEGMENT, entry[u'graphic_name'] )
            entry[u'image_url'] = image_url
            entry[u'url'] = u'%s://%s%s' % ( url_scheme, server_name, reverse(u'inscription_url', args=(entry[u'id'],)) )
            enhanced_list.append( entry )
        return enhanced_list

    # end class SolrHelper
