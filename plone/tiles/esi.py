# -*- coding: utf-8 -*-
from plone.tiles.interfaces import ESI_HEADER
from plone.tiles.interfaces import ESI_HEADER_KEY
from plone.tiles.interfaces import IESIRendered
from plone.tiles.interfaces import ITileType
from plone.tiles.tile import PersistentTile
from plone.tiles.tile import Tile
from Products.Five import BrowserView
from zExceptions import Unauthorized
from zope.component import queryUtility
from zope.interface import implementer

import os
import re
import transaction


try:
    from AccessControl.security import checkPermission
except ImportError:
    from zope.security import checkPermission


X_FRAME_OPTIONS = os.environ.get('PLONE_X_FRAME_OPTIONS', 'SAMEORIGIN')

HEAD_CHILDREN = re.compile(r'<head[^>]*>(.*)</head>', re.I | re.S)
BODY_CHILDREN = re.compile(r'<body[^>]*>(.*)</body>', re.I | re.S)

ESI_NAMESPACE_MAP = {'esi': 'http://www.edge-delivery.org/esi/1.0'}
_ESI_HREF = u'href="{url}/@@{esiMode}?{queryString}"'
ESI_TEMPLATE = u'''\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <body>
        <a class="_esi_placeholder" rel="esi" ''' + _ESI_HREF + '''></a>
    </body>
</html>
'''


def substituteESILinks(rendered):
    """Turn ESI links like <a class="_esi_placeholder" rel="esi" href="..." />
    into <esi:include /> links.

    ``rendered`` should be an HTML string.
    """

    rendered = re.sub(
        r'<html',
        '<html xmlns:esi="{0}"'.format(ESI_NAMESPACE_MAP['esi']),
        rendered,
        1
    )
    return re.sub(
        r'<a class="_esi_placeholder" rel="esi" href="([^"]+)"></a>',
        r'<esi:include src="\1" />',
        rendered
    )


class ConditionalESIRendering(object):
    head = False

    def render(self):
        raise NotImplemented(
            u"Override render() or set a class variable 'index' to point to "
            u"a view page template file")

    def __call__(self, *args, **kwargs):
        if self.request.getHeader(ESI_HEADER, 'false').lower() == 'true':
            mode = 'esi-body'
            if self.head:
                mode = 'esi-head'
            return ESI_TEMPLATE.format(
                url=(self.request.get('PATH_INFO') and
                     self.request.get('PATH_INFO').replace(' ', '%20') or
                     self.request.getURL()),
                queryString=self.request.get('QUERY_STRING', ''),
                esiMode=mode
            )
        # Do not hide AttributeError inside index()
        try:
            self.index
        except AttributeError:
            return self.render()
        return self.index(*args, **kwargs)


# Convenience base classes

@implementer(IESIRendered)
class ESITile(ConditionalESIRendering, Tile):
    """Convenience class for tiles using ESI rendering.

    Set ``head`` to True if this tile renders <head /> content. The
    default is to render <body /> content.
    """

    head = False


@implementer(IESIRendered)
class ESIPersistentTile(ConditionalESIRendering, PersistentTile):
    """Convenience class for tiles using ESI rendering.

    Set ``head`` to True if this tile renders <head /> content. The
    default is to render <body /> content.
    """

    head = False


# ESI views

class ESIHead(BrowserView):
    """Render the head portion of a tile independently.
    """

    def __call__(self):
        """Return the children of the <head> tag as a fragment.
        """
        # Check for the registered view permission
        try:
            type_ = queryUtility(ITileType, self.context.__name__)
            permission = type_.view_permission
        except AttributeError:
            permission = None
        if permission:
            if not checkPermission(permission, self.context):
                raise Unauthorized()

        if self.request.getHeader(ESI_HEADER):
            del self.request.environ[ESI_HEADER_KEY]

        document = self.context()  # render the tile

        # Disable the theme so we don't <html/>-wrapped
        self.request.response.setHeader('X-Theme-Disabled', '1')

        match = HEAD_CHILDREN.search(document)
        if not match:
            return document
        return match.group(1).strip()


class ESIBody(BrowserView):
    """Render the head portion of a tile independently.
    """

    def __call__(self):
        """Return the children of the <head> tag as a fragment.
        """
        # Check for the registered view permission
        try:
            type_ = queryUtility(ITileType, self.context.__name__)
            permission = type_.view_permission
        except AttributeError:
            permission = None
        if permission:
            if not checkPermission(permission, self.context):
                raise Unauthorized()

        if self.request.getHeader(ESI_HEADER):
            del self.request.environ[ESI_HEADER_KEY]

        document = self.context()  # render the tile

        # Disable the theme so we don't <html/>-wrapped
        self.request.response.setHeader('X-Theme-Disabled', '1')

        match = BODY_CHILDREN.search(document)
        if not match:
            return document
        return match.group(1).strip()


class ESIProtectTransform(object):
    """Replacement transform for plone.protect's ProtectTransform,
    because ESI tile responses' HTML should not be transformed to
    avoid wrapping them with <html>-tag
    """

    order = 9000

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def transform(self, result, encoding):
        from plone.protect.interfaces import IDisableCSRFProtection
        # clickjacking protection from plone.protect
        if X_FRAME_OPTIONS:
            if not self.request.response.getHeader('X-Frame-Options'):
                self.request.response.setHeader(
                    'X-Frame-Options', X_FRAME_OPTIONS)
        # drop X-Tile-Url
        if 'x-tile-url' in self.request.response.headers:
            del self.request.response.headers['x-tile-url']
        # ESI requests are always GET request and should not mutate DB
        # unless they provide IDisableCSRFProtection
        if not IDisableCSRFProtection.providedBy(self.request):
            transaction.abort()
        return None

    def transformBytes(self, result, encoding):
        return self.transform(result, encoding)

    def transformUnicode(self, result, encoding):
        return self.transform(result, encoding)

    def transformIterable(self, result, encoding):
        return self.transform(result, encoding)
