
import json, logging, pprint
import requests
from django.conf import settings as settings_project
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.views.decorators.cache import cache_page
from usep_app import settings_app, models


def search_form(request):
	sh = models.SolrHelper()
	results, facets, querystring = sh.query({u"*":u"*"}, {"rows":0}, search_form=True)


	field_list = ["text_genre", "object_type", "material", "language", "writing", "condition", "char"]
	f = []
	for x in field_list:
		f += [(x, facets[x])]
	return render(request, u'usep_templates/search_form.html', {"facets":f})

def results(request):

	q = dict(request.GET)

	sh = models.SolrHelper()

	results, facets, querystring = sh.query(q, {"rows": 4000})

	show_dates = u"notAfter" in querystring

	data_dict = {"q":q, "title":"Search", "facets":facets, "url":request.get_full_path(), "querystring":querystring, "show_dates":show_dates}
	if 'error' in results:
		data_dict['error'] = results['error']
	else:
		data_dict['results'] = sh.enhance_solr_data(results, request.META[u'wsgi.url_scheme'], request.get_host())

	return render(request, u'usep_templates/results.html', data_dict)
