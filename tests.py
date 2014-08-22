# -*- coding: utf-8 -*-

import json, logging, pprint
import usep_app
from django.test import TestCase
from usep_app import settings_app
# from usep_app.models import Repository
from usep_app.models import Collection, Publication, Publications

log = logging.getLogger(__name__)


### collection tests ###


### non django-model tests ###


class CollectionTest( TestCase ):

  def test_get_solr_data(self):
    c = Collection()
    inscription_list = c.get_solr_data( u'VA.Rich.MFA' )
    self.assertEqual( list, type(inscription_list) )
    self.assertEqual( dict, type(inscription_list[0]) )
    list_element_keys = sorted( inscription_list[0].keys() )
    self.assertEqual( [u'graphic_name', u'id', u'status'], list_element_keys )

  def test_enhance_solr_data(self):
    c = Collection()
    inscription_list = c.get_solr_data( u'VA.Rich.MFA' )
    enhanced_list = c.enhance_solr_data( solr_data=inscription_list, url_scheme=u'http', server_name=u'blah'  )
    self.assertEqual( list, type(enhanced_list) )
    self.assertEqual( dict, type(enhanced_list[0]) )
    list_element_keys = sorted( enhanced_list[0].keys() )
    self.assertEqual( [u'graphic_name', u'id', u'image_url', u'status', u'url'], list_element_keys )

  # end class CollectionTest()


# class Inscription2Test(TestCase):

#   def test_extract_inscription_data_a(self):  # more info
#     inscription_id = u'CA.Berk.UC.HMA.G.8-3898'
#     insc = Inscription2()
#     insc.run_xslt( inscription_id )
#     insc.update_xslt_html()
#     insc.extract_inscription_data()
#     self.assertEqual( u'Fragment', insc.extracted_data[u'attributes'][u'Condition'] )
#     self.assertEqual( [u'Smutny, R.J., Greek and Latin Inscriptions at Berkeley (1966): 6-7, no. 3, Pl. 5'], insc.extracted_data[u'bibl'] )

#   def test_extract_inscription_data_b(self):  # less info
#     inscription_id = u'CA.Berk.UC.HMA.G.8-4985'
#     insc = Inscription2()
#     insc.run_xslt( inscription_id )
#     insc.update_xslt_html()
#     insc.extract_inscription_data()
#     self.assertEqual( u'', insc.extracted_data[u'attributes'][u'Condition'] )
#     self.assertEqual( [u'Classical Attic Tombstones 3: 415', u'SEG 35 (1985): no. 202'], insc.extracted_data[u'bibl'] )

#   def test_extract_inscription_data_bib_only(self):
#     inscription_id = u'IL.Urb.UI.WHM.G.WHM1930.01.0001'
#     insc = Inscription2()
#     insc.run_xslt( inscription_id )
#     insc.update_xslt_html()
#     insc.extract_inscription_data()
#     self.assertEqual( {}, insc.extracted_data[u'attributes'] )
#     self.assertEqual( [u'BE (1973): no. 24', u'Kroll, J. H., Athenian Bronze Allotment Plates (1972): 124-126, no. 18'], insc.extracted_data[u'bibl'] )

#   # end class Inscription2Test()


class PublicationTest( TestCase ):

  def test_buildInscriptionList(self):
    pub = Publication()
    id_list = [ u'KY.Lou.SAM.L.1929.17.753', u'MI.AA.UM.KM.L.1038' ]
    pub.getPubData( id_list )
    # pprint.pprint( pub.inscription_entries )
    self.assertEqual( [u'graphic_name', u'id', u'status'], sorted(pub.inscription_entries[0].keys()) )

  # end class PublicationTest()


class PublicationsTest( TestCase ):

  def test_buildPubLists(self):
    data = [
     {u'bib_ids': [u'CAT_2', u'Rudolph'],
      u'bib_ids_types': [u'monograph'],
      u'bib_titles_all': [u'Classical Attic Tombstones',
                          u'Ancient Art from the V. G. Simkhovitch Collection'],
      u'id': u'IN.Bloom.IUAM.G.63.105.34'},
     {u'bib_ids': [u'CIL_VI'],
      u'bib_ids_types': [u'corpora'],
      u'bib_titles_all': [u'Corpus Inscriptionum Latinarum'],
      u'id': u'KY.Lou.SAM.L.1929.17.495'},
     {u'bib_ids': [u'CIL_VI'],
      u'bib_ids_types': [u'corpora'],
      u'bib_titles_all': [u'Corpus Inscriptionum Latinarum'],
      u'id': u'KY.Lou.SAM.L.1929.17.753'},
     {u'bib_ids': [u'CIL_VI', u'HSCP_Moore'],
      u'bib_ids_types': [u'corpora', u'journal'],
      u'bib_titles_all': [u'Corpus Inscriptionum Latinarum',
                          u'Harvard Studies in Classical Philology'],
      u'id': u'MA.Camb.HU.Sack.L.1977.216.1954'},
     {u'bib_ids': [u'AJP_Wilson5'],
      u'bib_ids_types': [u'journal'],
      u'bib_titles_all': [u'American Journal of Philology'],
      u'id': u'MD.Balt.JHU.L.99'},
     {u'bib_ids': [u'CIL_X', u'Tuck'],
      u'bib_ids_types': [u'corpora', u'monograph'],
      u'bib_titles_all': [u'Corpus Inscriptionum Latinarum',
                          u'Latin Inscriptions in the Kelsey Mueum: The Dennison and De Criscio Collections'],
      u'id': u'MI.AA.UM.KM.L.1038'},
     {u'bib_ids': [u'AJA_Dennison', u'ILS', u'Tuck'],
      u'bib_ids_types': [u'journal', u'corpora', u'monograph'],
      u'bib_titles_all': [u'American Journal of Archaeology',
                          u'Incriptiones Latinae Selectae',
                          u'Latin Inscriptions in the Kelsey Mueum: The Dennison and De Criscio Collections'],
      u'id': u'MI.AA.UM.KM.L.846'},
     {u'bib_ids': [u'CIL_XV'],
      u'bib_ids_types': [u'corpora'],
      u'bib_titles_all': [u'Corpus Inscriptionum Latinarum'],
      u'id': u'MO.Col.UM.MAA.L.83.263.4'},
     {u'bib_ids': [u'CIL_XV'],
      u'bib_ids_types': [u'corpora'],
      u'bib_titles_all': [u'Corpus Inscriptionum Latinarum'],
      u'id': u'NY.NY.CU.Butl.L.164'},
     {u'bib_ids': [u'Dentzer'],
      u'bib_ids_types': [u'monograph'],
      u'bib_titles_all': [u"Le motif du banquet couch\xe9 dans le Proche-Orient et le monde Grec du viie au ive si\xe8cle avant J.-C, Biblioth\xe8que des \xc9coles Francaises d'Ath\xe8nes et de Rome, vol. 246"],
      u'id': u'NY.NY.MMA.G.57.42'}]
    assert type(data) == list
    assert type(data[0]) == dict
    pubs = Publications()
    pubs.pubs_entries = data
    pubs.buildPubLists()
    # print u'pubs.corpora...'; pprint.pprint( pubs.corpora )
    # print u'pubs.journals...'; pprint.pprint( pubs.journals )
    # print u'pubs.monographs...'; pprint.pprint( pubs.monographs )
    # print u'pubs.corpora_dict...'; pprint.pprint( pubs.corpora_dict )
    # print u'pubs.journals_dict...'; pprint.pprint( pubs.journals_dict )
    # print u'pubs.monographs_dict...'; pprint.pprint( pubs.monographs_dict )
    # print u'pubs.master_pub_dict...'; pprint.pprint( pubs.master_pub_dict )
    self.assertEqual( type(pubs.corpora), list )
    self.assertEqual( type(pubs.journals), list )
    self.assertEqual( type(pubs.monographs), list )
    self.assertTrue( u'Corpus Inscriptionum Latinarum' in pubs.corpora )
    self.assertTrue( u'American Journal of Philology' in pubs.journals )
    self.assertTrue( u'Classical Attic Tombstones' in pubs.monographs )
    self.assertEqual( pubs.corpora_dict[u'Corpus Inscriptionum Latinarum'][0], u'KY.Lou.SAM.L.1929.17.495' )
    self.assertEqual( pubs.journals_dict[u'American Journal of Archaeology'][0], u'MI.AA.UM.KM.L.846' )
    self.assertEqual( pubs.monographs_dict[u'Ancient Art from the V. G. Simkhovitch Collection'][0], u'IN.Bloom.IUAM.G.63.105.34' )
    self.assertEqual( len(pubs.master_pub_dict.keys()), 9 )

  def test_buildPubLists_live_data(self):
    pubs = Publications()
    pubs.getPubData()  # makes solr call
    pubs.buildPubLists()
    self.assertEqual( type(pubs.corpora), list )
    self.assertEqual( type(pubs.journals), list )
    self.assertEqual( type(pubs.monographs), list )
    id_list = pubs.master_pub_dict[u"A Generation of Antiquities: The Duke Classical Collection 1964-1994"]
    # pprint.pprint( id_list )
    self.assertEqual( len(id_list), 3 )
    # self.assertTrue( u'Corpus Inscriptionum Latinarum' in pubs.corpora )
    # self.assertTrue( u'American Journal of Philology' in pubs.journals )
    # self.assertTrue( u'Classical Attic Tombstones' in pubs.monographs )
    # self.assertEqual( pubs.corpora_dict[u'Corpus Inscriptionum Latinarum'][0], u'KY.Lou.SAM.L.1929.17.495' )
    # self.assertEqual( pubs.journals_dict[u'American Journal of Archaeology'][0], u'MI.AA.UM.KM.L.846' )
    # self.assertEqual( pubs.monographs_dict[u'Ancient Art from the V. G. Simkhovitch Collection'][0], u'IN.Bloom.IUAM.G.63.105.34' )
    # print u'pubs.monographs_dict...'; pprint.pprint( pubs.monographs_dict )
    # print u'pubs.monographs...'; pprint.pprint( pubs.monographs )
    self.assertTrue( len(pubs.master_pub_dict.keys()) > 150 )

  # end class PublicationsTest()
