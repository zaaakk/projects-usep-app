# -*- coding: utf-8 -*-

from dj_projects_local_settings.usep_app_settings import *


## self-documentation
module_attributes = globals()  # http://docs.python.org/2/library/functions.html#globals
try:
    assert sorted( module_attributes.keys() ) == [
        u'COLLECTIONS_CACHE_SECONDS',   # integer; number of seconds
        u'INSCRIPTIONS_URL_SEGMENT',    # ustring; url to inscription-images directory; no trailing slash
        u'LOGIN_URL',                   # ustring; full url for login; allows simple enforced https for shib
        u'PERMITTED_ADMINS',            # list of ustrings; shib eppns
        u'PERMITTED_ADMIN_CONTACT',     # ustring; email address to be contacted to update permitted-admins
        u'PROJECT_APP',                 # ustring; i.e. u'project/app'; no trailing slash
        u'SERVER_NAME',                 # ustring; e.g. u'library.brown.edu'; could be obtained from request, would have to be passed from views to Region to Settlement to Institution
        u'SOLR_URL_BASE',               # ustring; url; include trailing slash
        u'SPOOFED_ADMIN',               # ustring; u'' in production; allows easy local non-shib login-testing

        u'TEMP_SAXONCE_FILE_URL',  # testing
        u'TEMP_SOURCE_XML_URL',    # testing
        u'TEMP_XIPR_URL',          # testing
        u'TEMP_XSL_URL',           # testing

        u'TRANSFORMER_URL',             # ustring; url; no trailing slash
        u'TRANSFORMER_XML_URL_SEGMENT', # ustring; can't reliably use XML_URL_SEGMENT because transformer may not be able to access dev boxes.
        u'TRANSFORMER_XSL_URL',         # ustring; can't reliably use settings_project.STATIC_URL because transformer may not be able to access dev boxes.
        u'XML_URL_SEGMENT',             # ustring; url to xml directory; no trailing slash
        u'__builtins__',                # irrelevant; standard module attribute
        u'__doc__',                     # ''
        u'__file__',                    # ''
        u'__name__',                    # ''
        u'__package__',                 # ''
        u'module_attributes',           # irrelevant; __this__ attribute
        ]
except Exception:                       # helps with debugging
    raise Exception, u'usep_app_settings module is instead returning: %s' %  sorted( module_attributes.keys() )
