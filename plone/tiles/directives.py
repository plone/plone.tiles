# -*- coding: utf-8 -*-
from plone.supermodel.directives import MetadataListDirective


IGNORE_QUERYSTRING_KEY = 'plone.tiles.ignore_querystring'


class ignore_querystring(MetadataListDirective):
    """Directive used to create fieldsets
    """
    key = IGNORE_QUERYSTRING_KEY

    def factory(self, name):
        return [name]
