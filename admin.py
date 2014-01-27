# -*- coding: utf-8 -*-

# from usep_app.models import FlatCollection, Repository
from usep_app.models import FlatCollection
from usep_app.models import AboutPage, ContactsPage, LinksPage, PublicationsPage, TextsPage
from django.contrib import admin
from django.db import models
from django.forms import Textarea


class FlatCollectionAdmin(admin.ModelAdmin):
  ordering = [ 'collection_code' ]
  list_display = [
    'id', 'collection_code', 'collection_name', 'collection_address', 'collection_url',
    'region_name', 'region_code', 'settlement_code', 'institution_code', 'repository_code' ]  # removed 'collection_description' because it was so long.
  list_filter = [ 'region_code', 'settlement_code' ]
  search_fields = [ 'collection_code', 'collection_name', 'collection_address',
    'region_name', 'region_code', 'settlement_code', 'institution_code', 'repository_code' ]
  readonly_fields = [ 'id' ]
  # formfield_overrides = {
  #   models.TextField: { 'widget': Textarea(attrs={'rows':4, 'cols':40}) },  # trying to handle long descriptions in admin overview, but this only applies when editing an individual entry.
  # }


# class RepositoryAdmin(admin.ModelAdmin):
#   ordering = [ 'code' ]
#   list_display = [ 'code', 'name', 'institution_code', 'settlement_code', 'region_code' ]
#   list_filter = [ 'code', 'name', 'institution_code', 'settlement_code', 'region_code' ]
#   readonly_fields = [ 'code', 'institution_code', 'settlement_code', 'region_code' ]


admin.site.register( FlatCollection, FlatCollectionAdmin )
# admin.site.register( Repository, RepositoryAdmin )

## static pages
admin.site.register( AboutPage )
admin.site.register( ContactsPage )
admin.site.register( LinksPage )
admin.site.register( PublicationsPage )
admin.site.register( TextsPage )
