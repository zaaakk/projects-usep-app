from django import template
from usep_app import models

register = template.Library()

v = models.Vocab()

@register.filter( name=u'tax' )
def tax( name ):
  return v[name]
