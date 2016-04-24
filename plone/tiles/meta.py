# -*- coding: utf-8 -*-
from plone.tiles.interfaces import ITileType
from plone.tiles.tile import Tile
from plone.tiles.type import TileType
from Products.Five.browser.metaconfigure import page
from zope import schema
from zope.component.zcml import utility
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import MessageID
from zope.configuration.fields import Path
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.security.zcml import Permission


class ITileDirective(Interface):
    """Directive which registers a new type of tile
    """

    name = schema.DottedName(
        title=u"Name",
        description=u"A unique, dotted name for the tile",
        required=True,
    )

    title = MessageID(
        title=u"Title",
        description=u"A user friendly title, used when configuring the tile",
        required=False
    )

    description = MessageID(
        title=u"Description",
        description=u"A longer summary of the tile's purpose and function",
        required=False
    )

    icon = MessageID(
        title=u"Icon",
        description=u"Image that represents tile purpose and function",
        required=False
    )

    add_permission = Permission(
        title=u"Add permission",
        description=u"Name of the permission required to instantiate "
                    u"this tile",
        required=False,
    )

    edit_permission = Permission(
        title=u"Edit permission",
        description=u"Name of the permission required to edit this tile",
        required=False,
    )

    delete_permission = Permission(
        title=u"Delete permission",
        description=u"Name of the permission required to delete this tile",
        required=False,
    )

    schema = GlobalInterface(
        title=u"Configuration schema for the tile",
        description=u"This is used to create standard add/edit forms",
        required=False,
    )

    for_ = GlobalObject(
        title=u"The interface or class this tile is available for",
        required=False,
    )

    layer = GlobalInterface(
        title=u"The layer the tile is available for",
        required=False
    )

    class_ = GlobalObject(
        title=u"Class",
        description=u"Class implementing this tile",
        required=False
    )

    template = Path(
        title=u"The name of a template that renders this tile",
        description=u"Refers to a file containing a page template",
        required=False,
    )

    permission = Permission(
        title=u"View permission",
        description=u"Name of the permission required to view this item",
        required=True,
    )


def tile(_context, name, title=None, description=None, icon=None,
         add_permission=None, edit_permission=None, delete_permission=None,
         schema=None, for_=None, layer=None, class_=None, template=None,
         permission=None):
    """Implements the <plone:tile /> directive
    """
    if (
        title is not None or
        description is not None or
        icon is not None or
        add_permission is not None or
        schema is not None
    ):
        if title is None or add_permission is None:
            raise ConfigurationError(
                u"When configuring a new type of tile, 'title' and "
                u"'add_permission' are required")
        type_ = TileType(
            name,
            title,
            add_permission,
            permission,
            edit_permission=edit_permission,
            delete_permission=delete_permission,
            description=description,
            icon=icon,
            schema=schema
        )

        utility(_context, provides=ITileType, component=type_, name=name)

    if (
        for_ is not None or
        layer is not None or
        class_ is not None or
        template is not None
    ):
        if class_ is None and template is None:
            raise ConfigurationError(
                u"'class' or 'template' must be given when configuring a tile."
            )

        if for_ is None:
            for_ = Interface
        if layer is None:
            layer = IDefaultBrowserLayer

        if class_ is None:
            class_ = Tile

        page(_context, name=name, permission=permission, for_=for_,
             layer=layer, template=template, class_=class_)
