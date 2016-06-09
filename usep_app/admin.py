# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .models import FlatCollection
from django.contrib import admin
from .models import AboutPage, ContactsPage, LinksPage, PublicationsPage, TextsPage



class FlatCollectionAdmin( admin.ModelAdmin ):
    # date_hierarchy = 'sent'
    # list_display = [ 'sent', 'sender', 'email' ]
    ordering = [ '-id' ]


admin.site.register( FlatCollection, FlatCollectionAdmin )

## static pages
admin.site.register( AboutPage )
admin.site.register( ContactsPage )
admin.site.register( LinksPage )
admin.site.register( PublicationsPage )
admin.site.register( TextsPage )
