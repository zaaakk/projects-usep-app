# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os


LOGIN_URL = unicode( os.environ['USEPWEB__LOGIN_URL'] )

SOLR_URL_BASE = unicode( os.environ['USEPWEB__SOLR_URL_BASE'] )

DISPLAY_PUBLICATIONS_BIB_URL = unicode( os.environ['USEPWEB__DISPLAY_PUBLICATIONS_BIB_URL'] )

DISPLAY_PUBLICATIONS_XSL_URL = unicode( os.environ['USEPWEB__DISPLAY_PUBLICATIONS_XSL_URL'] )  # views.publications()
