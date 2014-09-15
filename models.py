# -*- coding: utf-8 -*-

import json, logging, os, pprint
from operator import itemgetter  # for a comparator sort

import requests
from django.conf import settings as settings_project
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import smart_unicode
from usep_app import settings_app

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


class Collection(object):
    """ Handles code to display the inscriptions list for a given collection. """

    def get_solr_data( self, collection ):
        """ Queries solr for collection info. """
        payload = {
            u'q': collection,
            u'fl': u'id,status,graphic_name',
            u'start': u'0',
            u'rows': u'99000',
            u'wt': u'json',
            u'indent': u'on', }
        r = requests.get( settings_app.SOLR_URL_BASE, params=payload )
        d = json.loads( r.content.decode(u'utf-8', u'replace') )
        sorted_doc_list = sorted( d[u'response'][u'docs'], key=itemgetter(u'id') )  # sorts the doc-list on dict key 'id'
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
        return enhanced_list

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

    def getPubData( self, id_list ):
        """
        Builds solr query from inscription-id list stored in session by Publications.buildPubLists().
        We have the ids already; we just need the status (possible TODO: store the status when the id-list is originally built).
        Loop used because a large list can return a solr 'too many boolean clauses' error
        """
        log.debug( u'len(id_list): %s' % len(id_list) )
        log.debug( u'id_list: %s' % id_list )

        # log.debug( u'self.inscription_entries START: %s' % self.inscription_entries )
        log.debug( u'len(self.inscription_entries) START: %s' % len(self.inscription_entries) )
        for i in range( 0, len(id_list), 500 ):  # needed
            list_chunk = id_list[i:i + 500]
            ## make solr call
            q_string = u''
            for i, entry in enumerate( list_chunk ):
                if i == 0:
                    q_string = u'id:%s' % entry
                else:
                    q_string = u'%s OR id:%s' % ( q_string, entry )
            sh = SolrHelper()
            payload = dict( sh.default_params.items() + {
                u'q': q_string,
                u'rows': u'99999',
                u'fl': u'id,graphic_name,status',
                u'sort': u'id asc' }.items()
                )
            r = requests.post( settings_app.SOLR_URL_BASE, payload )
            solr_response = r.content.decode(u'utf-8', u'replace')
            log.debug( u'this pubn_solr_url: %s' % r.url )
            # log.debug( u'this pubn_solr_response: %s' % solr_response )
            self.pub_solr_urls.append( r.url )
            self.pub_solr_responses.append( solr_response )
            jdict = json.loads( solr_response )
            for item in jdict[u'response'][u'docs']:
                self.inscription_entries.append( item )
        self.inscription_count = len( self.inscription_entries )
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
        u'wt': u'json' }
