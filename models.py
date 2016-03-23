# -*- coding: utf-8 -*-

import json, logging, os, pprint
from operator import itemgetter  # for a comparator sort

import requests
from django.conf import settings as settings_project
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import smart_unicode
from usep_app import settings_app

from django.utils.http import urlencode

from lxml import etree

import string

log = logging.getLogger(__name__)



### django-db collection class ###


class FlatCollection( models.Model ):
    """ Represents non-hierarchical collection. """
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
        from usep_app.models import FlatCollection
        q = FlatCollection.objects.values('region_code').distinct()  # type: <class 'django.db.models.query.ValuesQuerySet'>; eg: [{'region_code': u'CA'}, {'region_code': u'MA'}]
        region_codes = []
        for entry in q:
            region_codes.append( entry.values()[0] )
        return sorted( region_codes )

    # end class FlatCollection


### django-db models for static pages ###


class AboutPage(models.Model):
    title_page = models.CharField( blank=True, max_length=100 )
    title_content = models.CharField( blank=True, max_length=100 )
    content = models.TextField( blank=True, help_text='HTML allowed.' )
    def __unicode__(self):
        return smart_unicode( self.title_page, u'utf-8', u'replace' )
    class Meta:
        verbose_name_plural = u'About page fields'


class TextsPage(models.Model):
    title_page = models.CharField( blank=True, max_length=100 )
    title_content = models.CharField( blank=True, max_length=100 )
    content = models.TextField( blank=True, help_text='HTML allowed.' )
    def __unicode__(self):
        return smart_unicode( self.title_page, u'utf-8', u'replace' )
    class Meta:
        verbose_name_plural = u'Texts page fields'


class LinksPage(models.Model):
    title_page = models.CharField( blank=True, max_length=100 )
    title_content = models.CharField( blank=True, max_length=100 )
    content = models.TextField( blank=True, help_text='HTML allowed.' )
    def __unicode__(self):
        return smart_unicode( self.title_page, u'utf-8', u'replace' )
    class Meta:
        verbose_name_plural = u'Links page fields'


class ContactsPage(models.Model):
    title_page = models.CharField( blank=True, max_length=100 )
    title_content = models.CharField( blank=True, max_length=100 )
    content = models.TextField( blank=True, help_text='HTML allowed.' )
    def __unicode__(self):
        return smart_unicode( self.title_page, u'utf-8', u'replace' )
    class Meta:
        verbose_name_plural = u'Contacts page fields'


class PublicationsPage(models.Model):
    title_page = models.CharField( blank=True, max_length=100 )
    title_content = models.CharField( blank=True, max_length=100 )
    content = models.TextField( blank=True, help_text='HTML allowed.' )
    def __unicode__(self):
        return smart_unicode( self.title_page, u'utf-8', u'replace' )
    class Meta:
        verbose_name_plural = u'Publication page fields'


### other non-db classes ###

# Function to pass to sorted() to sort the list of documents by weird free-form ids
# essentially splits them into numeric and non-numeric keys and returns whatever
# set it was able to break up
def id_sort(doc):
    idno = doc[u'msid_idno']

    # IN THE FUTURE:
    # add to this string to add new characters to split tokens over (splits over "." by default)
    split_characters = "-,/"
    # add to this string to add new characters that should be removed (e.g. "#")
    remove_characters = "#"

    for c in split_characters:
        idno = idno.replace(c, ".")
    for c in remove_characters:
        idno = idno.replace(c, "")

    keylist = []
    for x in idno.split("."):
        try:
            keylist += [int(x)]
        except ValueError:

            tokens = break_token(x)
            keylist += tokens

    return tuple(keylist)

# Break a mixed numeric/text token into numeric/non-numeric parts. Helper for id_sort
def break_token(token):
    idx1 = 0
    idx2 = 0
    parts = []
    numeric = (token[0] in string.digits) # True if we start with a numeric token, false otherwise

    # Loop through string and add subtokens to parts as necessary
    for c in token:
        condition = token[idx2] in string.digits
        if not numeric:
            condition = not condition


        if condition:
            idx2 += 1
        else:
            parts += [int(token[idx1:idx2])] if numeric else [token[idx1:idx2]]
            idx1 = idx2
            idx2 += 1
            numeric = not numeric

    parts += [token[idx1:idx2]]
    return parts

def separate_into_languages(docs):

    # Language value/display pairs as of 3/2016
    language_pairs = {
        u"lat": u"Latin",
        u"grc": u"Greek",
        u"la": u"Latin",
        u"la-Grek": u"Latin written in Greek",
        u"lat-Grek":u"Latin written in Greek",
        u"etr":u"Etruscan",
        u"xrr":u"Raetic",
        u"und": u"Undecided",
        u"unknown": u"Unknown"
    }

    # result = {}
    # for doc in docs:
    #     if doc[u'language'] in result:  # 2016-02-09: when doc['language'] is a list, result is `TypeError -- unhashable type: 'list'`
    #         result[doc[u'language']][u'docs'] += [doc]
    #     else:
    #         result[doc[u'language']] = {u'docs': [doc], u'display': language_pairs.get(doc[u'language'], doc[u"language"])}

    result = {}
    for doc in docs:
        language = doc.get('language', u'')
        language = language[0] if type(language) == list else language
        if language in result:
            result[language][u'docs'] += [doc]
        else:
            result[language] = {u'docs': [doc], u'display': language_pairs.get(language, language)}

    # Actual display pairs used for convenience
    d = dict([(lang, language_pairs.get(lang, lang)) for lang in result])

    return (result, len(docs), d)

class Collection(object):
    """ Handles code to display the inscriptions list for a given collection. """

    def get_solr_data( self, collection ):
        """ Queries solr for collection info. """
        payload = {
            u'q': collection,
            u'fl': u'id,status,graphic_name,language,msid_idno',
            u'start': u'0',
            u'rows': u'99000',
            u'wt': u'json',
            u'indent': u'on', }
        r = requests.get( settings_app.SOLR_URL_BASE, params=payload )
        d = json.loads( r.content.decode(u'utf-8', u'replace') )
        sorted_doc_list = sorted( d[u'response'][u'docs'], key=id_sort )  # sorts the doc-list on dict key 'msid_idno'

        return sorted_doc_list

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
        return separate_into_languages(enhanced_list)

    # end class Collection()


class DisplayInscriptionHelper( object ):
    """ Helper for views.display_inscription() """

    # def build_custom_static_url( self, project_static_url, hostname ):
    #     """ Updates settings_PROJECT STATIC_URL if needed.
    #         Returns url.
    #         """
    #     custom_static_url = project_static_url
    #     if hostname.lower() == u'usepigraphy.brown.edu':
    #       custom_static_url = custom_static_url.replace( 'library.brown.edu', 'usepigraphy.brown.edu' )  # so js saxon-ce works as expected
    #     return custom_static_url

    def build_source_xml_url( self, url_pattern, is_secure, hostname, inscription_id ):
        """ Returns url to inscription xml. """
        scheme = u'https' if ( is_secure == True ) else u'http'
        url = url_pattern.replace( u'SCHEME', scheme )
        url = url.replace( u'HOSTNAME', hostname )
        url = url.replace( u'INSCRIPTION_ID', inscription_id )
        return url

    def build_context( self, hostname, custom_static_url, inscription_id, source_xml_url, xsl_url, saxonce_url, xipr_url ):
        """ Returns context dict. """
        context = {
          u'custom_static_url': self.update_host( hostname, custom_static_url ),
          u'inscription_id': inscription_id,
          u'source_xml_url': self.update_host( hostname, source_xml_url ),
          u'xsl_url': self.update_host( hostname, xsl_url ),
          u'saxonce_file_url': self.update_host( hostname, saxonce_url ),
          u'xipr_url': self.update_host( hostname, xipr_url )
          }
        return context

    def update_host( self, hostname, url ):
        """ Updates url if needed.
            Allows saxonce and ajax references to work with both `library.brown.edu` and `usepigraphy.brown.edu` urls. """
        if hostname.lower() == u'usepigraphy.brown.edu':
            url = url.replace( 'library.brown.edu', 'usepigraphy.brown.edu' )
        return url

    # end class DisplayInscriptionHelper()


# class DisplayInscriptionHelper( object ):
#     """ Helper for views.display_inscription() """

#     def build_custom_static_url( self, project_static_url, hostname ):
#         """ Updates settings_PROJECT STATIC_URL if needed.
#             Returns url.
#             """
#         custom_static_url = project_static_url
#         if hostname.lower() == u'usepigraphy.brown.edu':
#           custom_static_url = custom_static_url.replace( 'library.brown.edu', 'usepigraphy.brown.edu' )  # so js saxon-ce works as expected
#         return custom_static_url

#     def build_source_xml_url( self, url_pattern, is_secure, hostname, inscription_id ):
#         """ Returns url to inscription xml. """
#         scheme = u'https' if ( is_secure == True ) else u'http'
#         url = url_pattern.replace( u'SCHEME', scheme )
#         url = url.replace( u'HOSTNAME', hostname )
#         url = url.replace( u'INSCRIPTION_ID', inscription_id )
#         return url

#     def build_context( self, custom_static_url, inscription_id, source_xml_url, xsl_url, saxonce_url, xipr_url ):
#         """ Returns context dict. """

#         context = {
#           u'custom_static_url': custom_static_url,
#           u'inscription_id': inscription_id,
#           u'source_xml_url': source_xml_url,
#           u'xsl_url': xsl_url,
#           u'saxonce_file_url': saxonce_url,
#           u'xipr_url': xipr_url
#           }
#         return context

#   # end class DisplayInscriptionHelper()

class Publication(object):

    def __init__(self):
        self.title = u''
        self.inscription_count = 0
        self.inscription_entries = []
        self.inscription_images = []  # used for thumbnails
        self.pub_solr_urls = []
        self.pub_solr_responses = []

    def getPubData( self, pub_id ):
        """
        Retrieves inscriptions with the given bib_id.
        """

        log.debug( u'len(self.inscription_entries) START: %s' % len(self.inscription_entries) )

        sh = SolrHelper()

        payload = dict( sh.default_params.items() + {
                u'q':u'bib_ids:{0}'.format(pub_id),
                u'rows':u'99999',
                u'fl': u'id,graphic_name,status',
                u'sort': u'id asc'}.items()
                )
        r = requests.post( settings_app.SOLR_URL_BASE, payload )
        solr_response = r.content.decode('utf-8', 'replace')
        self.pub_solr_urls.append( r.url )
        self.pub_solr_responses.append( solr_response )
        json_resp = json.loads(solr_response)
        
        self.inscription_entries = json_resp[u'response'][u'docs']
        self.inscription_count = json_resp[u'response'][u'numFound']

        log.debug( u'self.inscription_entries END: %s' % self.inscription_entries[0:10] )
        return

    def buildInscriptionList( self, url_scheme, server_name ):
        """Adds item-url to inscription-dict list."""
        for item in self.inscription_entries:
            item[u'url'] = u'%s://%s%s' % ( url_scheme, server_name, reverse(u'inscription_url', args=(item[u'id'],)) )
        return

    def makeImageUrls( self ):
        """Adds image_url to inscription-dict list."""
        for item in self.inscription_entries:
            image_url = None
            if u'graphic_name' in item.keys():
                image_url = u'%s/%s' % ( settings_app.INSCRIPTIONS_URL_SEGMENT, item[u'graphic_name'] )
            item[u'image_url'] = image_url
        return

    # end class Publication()


class Publications(object):

    def __init__(self):
        self.corpora = []  # list for display
        self.corpora_dict = {}  # dict of key=title & value=inscription_id list
        self.journals = []
        self.journals_dict = {}
        self.monographs = []
        self.monographs_dict = {}
        # self.monographs_citation = {} # dict of key=title & value=citation in format <author>, <title>. [<bib_id>]
        self.master_pub_dict = {}
        self.pubs_solr_url = None
        self.pubs_solr_response = None
        self.pubs_entries = None

    def getPubData(self):
        """Gets solr publication data for self.buildPubLists()"""
        #print "models.py: Publications: getPubData"

        sh = SolrHelper()
        payload = dict( sh.default_params.items() + {
            u'q': u'bib_ids_types:*',
            u'rows': u'99999',
            u'fl': u'id, bib_ids, bib_ids_types, bib_titles, bib_titles_all, bib_authors, status' }.items()
            )

        #print "\tAbout to make request!"
        r = requests.get( settings_app.SOLR_URL_BASE, params=payload )

        #print "\tReturned from the get request"
        log.debug( u'publications solr call: %s' % r.url )
        self.pubs_solr_url = r.url
        self.pubs_solr_response = r.content.decode( u'utf-8', u'replace' )
        jdict = json.loads( self.pubs_solr_response )
        log.debug( u'publications solr query result dict keys.response: %s' % jdict.keys() )
        log.debug( u'publications solr query result dict["response"] keys: %s' % jdict[u'response'].keys() )
        log.debug( u'publications solr query result dict["response"]["numFound"]: %s' % jdict[u'response'][u'numFound'] )
        log.debug( u'publications solr query result dict["response"]["docs"][0]: %s' % jdict[u'response'][u'docs'][0:5] )
        self.pubs_entries = jdict[u'response'][u'docs']
        # log.debug( u'self.pubs_entries: %s' % self.pubs_entries )

    def buildPubLists(self):
        """Builds list of publications grouped by type."""
        # log.debug( u'self.pubs_entries: %s' % self.pubs_entries )
        log.debug( u'len( self.pubs_entries ): %s' % len( self.pubs_entries ) )
        corpora_dict = {}; journal_dict = {}; monograph_dict = {}  # temp holders

        # #print len(self.pubs_entries)
        # #print self.pubs_entries.__class__
        # #print str(self.pubs_entries[1:4])

        for entry in self.pubs_entries:  # an entry can contain multiple bibs
            # log.debug( u'entry being processed: %s' % entry )
            ## make separate bib entries

            # #print "\n" + str(entry)

            temp_bibs = []
            last_bib_type = None
            for i, bib_id in enumerate( entry[u'bib_ids'] ):
                try:
                    last_bib_type = entry[u'bib_ids_types'][i]  # first should always succeed
                    #print last_bib_type + "; bib_id: " + bib_id + "; i: " + i
                except:
                    pass
                try:
                    bib_title = entry[u'bib_titles_all'][i]
                except:
                    bib_title = u'title not found for bib_id "%s"' % bib_id
                try:
                    bib_status = entry[u'status']
                except:
                    bib_status = u'no_status'
                # try:
                #     #only monographs have a single author
                #     if (last_bib_type == 'monograph'):
                #         id_types_list = entry[u'bib_ids_types'] #get the list of id types
                #         monograph_indices_before = [j for j, element in enumerate(id_types_list[0:i]) if element == 'monograph'] #finds the indices for all monographs before this one in the same entry
                #         num_monographs_before = len([id_types_list[k] for k in monograph_indices_before])
                #         num_monographs_index_modifier = num_monographs_before - 1
                #         index = num_monographs_index_modifier + i
                #         bib_author = entry[u'bib_authors'][index]
                #     #journals and corpora have multiple authors
                #     else:
                #         bib_author = u'multiple_authors'
                # except:
                #     bib_author = u'no_author'
                # try:
                #     bib_id = entry[u'bib_ids'][i]
                # except:
                #     try:
                #         bib_id = entry[u'bib_ids'][0] # try again and just use the first bib_id
                #     except:
                #         bib_id = u'no_bib_id'
                temp_bibs.append( {
                    u'bib_id': bib_id,
                    u'bib_title': bib_title,
                    u'bib_type': last_bib_type,
                    u'id': entry[u'id'],  # the inscription_id
                    u'status': bib_status
                    # u'bib_author': bib_author,
                    # u'bib_id': bib_id
                    } )
            # log.debug( u'temp_bibs: %s' % temp_bibs )

            # #print len(temp_bibs)
            # #print temp_bibs.__class__
            # #print str(temp_bibs[1:4])


            ## categorize by bib_type
            for bib in temp_bibs:
                ## update master dict
                # self.master_pub_dict[ bib[u'bib_title'] ] = { u'id': bib[u'id'], u'status': bib[u'status'] }
                if bib[u'bib_title'] in self.master_pub_dict.keys():
                    self.master_pub_dict[ bib[u'bib_title'] ].append( bib[u'id'] )
                else:
                    self.master_pub_dict[ bib[u'bib_title'] ] = [ bib[u'id'] ]
                ## update type-dicts
                if bib['bib_type'] == u'corpora':
                    if bib[u'bib_title'] in corpora_dict.keys():
                        corpora_dict[ bib[u'bib_title'] ].append( bib[u'id'] )
                    else:
                        corpora_dict[ bib[u'bib_title'] ] = [ bib[u'id'] ]
                elif bib['bib_type'] == u'journal':
                    if bib[u'bib_title'] in journal_dict.keys():
                        journal_dict[ bib[u'bib_title'] ].append( bib[u'id'] )
                    else:
                        journal_dict[ bib[u'bib_title'] ] = [ bib[u'id'] ]
                elif bib['bib_type'] == u'monograph':
                    # log.debug( u'bib_type is monograph' )
                    if bib[u'bib_title'] in monograph_dict.keys():
                        monograph_dict[ bib[u'bib_title'] ].append( bib[u'id'] )
                    else:
                        monograph_dict[ bib[u'bib_title'] ] = [ bib[u'id'] ]

                # log.debug( u'monograph_dict is now: %s' % monograph_dict )
        ## store
        self.corpora_dict = corpora_dict
        self.corpora = sorted( self.corpora_dict.keys() )
        self.journals_dict = journal_dict
        self.journals = sorted( self.journals_dict.keys() )
        self.monographs_dict = monograph_dict
        self.monographs = sorted( self.monographs_dict.keys() )

        # #print ("\n'Classical Attic Tombstones' in self.corpora_dict.keys() " + str('Classical Attic Tombstones' in self.corpora_dict.keys()))
        # print str([j for j, element in enumerate(self.corpora_dict.keys()) if element == 'Classical Attic Tombstones'])
        # print str(self.corpora_dict[('Classical Attic Tombstones')])

        # print ("\n'Classical Attic Tombstones' in self.journals_dict.keys() " + str('Classical Attic Tombstones' in self.journals_dict.keys()))
        # print str([j for j, element in enumerate(self.journals_dict.keys()) if element == 'Classical Attic Tombstones'])
        # print str(self.journals_dict[('Classical Attic Tombstones')])

        # print ("\n'Classical Attic Tombstones' in self.monographs_dict.keys() " + str('Classical Attic Tombstones' in self.monographs_dict.keys()))
        # print str([j for j, element in enumerate(self.monographs_dict.keys()) if element == 'Classical Attic Tombstones'])
        # print str(self.monographs_dict[('Classical Attic Tombstones')])



        # log.debug( u'corpora list before sort: %s' % self.corpora )
        return

    # end class Publications()


class SolrHelper(object):
    default_params = {
        u'start': u'0',
        u'indent': u'on',
        u'facet': u'on',
        u'facet.mincount': u'1',
        u'facet.limit':u'-1',
        u'wt': u'json' }
    solr_url = settings_app.SOLR_URL_BASE

    default_facets = ["condition", "decoration", "fake", "language", "material", 
        "object_type", "text_genre", "writing", "status", "char", "name"]

    def __init__(self):
        self.vocab = Vocab()

    def makeSolrQuery(self, q_obj):
        fields = []
        for f in q_obj:
            if f.startswith(u"facet_"):
                fields += [u"({0}:{1})".format(f[6:], q_obj[f][0])]
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

    def query(self, q_obj, params={}):
        q = self.makeSolrQuery(q_obj)
        params = dict(params.items() + self.default_params.items())
        params[u'facet.mincount'] = "1"
        params[u'facet.field'] = self.default_facets
        params[u'q'] = q

        r = requests.get(self.solr_url, params=params)
        resp = r.json
        if "error" in resp:
            return resp, None, None
        return self.add_collection(resp['response']['docs']), self.facetDisplay(resp['facet_counts']['facet_fields']), q

    def facetDisplay(self, facet_dict):
        """Make a display dict from a solr facet result, parsing the counts into a dict"""
        facet_displays = dict()
        for field in facet_dict:
            facet_displays[field] = dict()
            counts = facet_dict[field]

            for i in range(0,len(counts), 2):
                facet_displays[field][counts[i]] = counts[i+1]

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

class Vocab(object):
    """Matches controlled values to display values."""
    tax_url = settings_app.DISPLAY_PUBLICATIONS_BIB_URL.replace("titles.xml", "include_taxonomies.xml")

    fieldNames = {
        u"condition": u"Condition",
        u"decoration": u"Decoration",
        u"fake": u"Fake",
        u"language": u"Language",
        u"material": u"Material",
        u"object_type":u"Type of Object",
        u"text_genre": u"Genre",
        u"writing": u"Writing",
        u"status": u"Transcription Status",
        u"char": u"Special Characters",
        u"name": u"Names",
        u"metadata": u"Metadata",
        u"transcription": u"Fully Transcribed",
        u"bib_only": u"Citations",
    }

    language_pairs = {
        u"lat": u"Latin",
        u"grc": u"Greek",
        u"la": u"Latin",
        u"la-Grek": u"Latin written in Greek",
        u"lat-Grek":u"Latin written in Greek",
        u"etr":u"Etruscan",
        u"xrr":u"Raetic",
        u"und": u"Undecided",
        u"unknown": u"Unknown"
    }
    
    def __init__(self):
        r = requests.get(self.tax_url)
        self.xml = etree.fromstring(r.content)

        self.control_vals = etree.XPath("//t:category/@xml:id", namespaces={"t":"http://www.tei-c.org/ns/1.0"})(self.xml)

        self.map = dict()

        for val in self.control_vals:
            display = etree.XPath("//t:category[@xml:id='{0}']/t:catDesc".format(val), namespaces={"t":"http://www.tei-c.org/ns/1.0"})(self.xml)
            if display:
                self.map[val] = display[0].text

        self.map = dict(self.map.items() + self.fieldNames.items() + self.language_pairs.items())

    def __getitem__(self, i):
        i = i.replace("#", "")
        if i in self.map:
            return self.map[i]
        else:
            return i
        
