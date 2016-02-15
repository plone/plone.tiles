# -*- coding: utf-8 -*-
from plone.tiles.interfaces import ITileType
from zope.interface import implements


class TileType(object):
    """A utility that describes a type of tile
    """

    implements(ITileType)

    def __init__(self, name, title, add_permission, edit_permission=None,
                 delete_permission=None, description=None, icon=None,
                 schema=None):

        if delete_permission is None:
            delete_permission = add_permission

        if edit_permission is None:
            edit_permission = add_permission

        self.__name__ = name
        self.title = title
        self.add_permission = add_permission
        self.edit_permission = edit_permission
        self.delete_permission = delete_permission
        self.description = description
        self.icon = icon
        self.schema = schema

    def __repr__(self):
        return u'<TileType {0} ({1})>'.format(self.__name__, self.title,)
