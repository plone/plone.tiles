# -*- coding: utf-8 -*-
from plone.tiles.data import encode
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from six.moves.urllib import parse
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL

_safe = '@+'


class BaseTileAbsoluteURL(AbsoluteURL):
    """Convenience base class
    """

    def __str__(self):
        tile = self.context
        request = self.request

        tid = tile.id
        name = tile.__name__
        context = tile.__parent__

        if name is None or context is None:
            raise TypeError('Insufficient context to determine URL')

        tileFragment = '@@' + parse.quote(name.encode('utf-8'), _safe)
        if tid:
            tileFragment += '/' + parse.quote(tid.encode('utf-8'), _safe)

        absolute_url = getMultiAdapter((context, request), IAbsoluteURL)
        try:
            tileFragment = '/'.join([str(absolute_url), tileFragment])
        except TypeError:  # Not enough context to get URL information
            pass

        return tileFragment

    def breadcrumbs(self):
        tile = self.context
        request = self.request

        tid = tile.id
        name = tile.__name__
        context = tile.__parent__

        tileFragment = '@@' + parse.quote(name.encode('utf-8'), _safe)
        if tid:
            tileFragment += '/' + parse.quote(tid.encode('utf-8'), _safe)

        base = tuple(
            getMultiAdapter((context, request), IAbsoluteURL).breadcrumbs())
        base += (
            {
                'name': name,
                'url': '/'.join([base[-1]['url'], tileFragment]),
            },
        )

        return base


class TransientTileAbsoluteURL(BaseTileAbsoluteURL):
    """Absolute URL for a transient tile. Includes the tile traverser and
    tile data encoded in the query string.
    """

    def __str__(self):
        url = super(TransientTileAbsoluteURL, self).__str__()
        manager = ITileDataManager(self.context)

        # Transient looking tile with id is only really transient
        # if it caches its decoded query data in request annotations
        transient = manager.storage == IAnnotations(self.request)

        # When transient looking tile with id is not really transient,
        # its data should not be encoded into query string
        if self.context.id and not transient:
            return url

        # All tiles don't need / have configuration data at all.
        data = manager.get()
        if not data:
            return url

        # But when configuration data is really read from query string
        # and not persisted, it should also be kept in query string
        tileType = queryUtility(ITileType, name=self.context.__name__)
        if tileType is not None and tileType.schema is not None:
            if '?' in url:
                url += '&' + encode(data, tileType.schema)
            else:
                url += '?' + encode(data, tileType.schema)
        return url


class PersistentTileAbsoluteURL(BaseTileAbsoluteURL):
    """Absolute URL for a persitent tile. Includes the tile traverser, but no
    tile data encoded in the query string.
    """
