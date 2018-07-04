# -*- coding: utf-8 -*-
from plone.tiles.interfaces import IPersistentTile
from plone.tiles.interfaces import ITile
from plone.tiles.interfaces import ITileDataManager
from Products.Five import BrowserView
from zExceptions import Forbidden
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.traversing.browser.absoluteurl import absoluteURL


@implementer(ITile)
class Tile(BrowserView):
    """Basic implementation of a transient tile. Subclasses should override
    __call__ or set an 'index' variable to point to a view page template file.

    The tile is basically a browser view, with the following enhancements:

    * The attribute `data` can be used to read the tile data, as returned by
      `ITileDataManager(tile).get()`. This value is cached when it is first
      read.
    * The attribute `url` can be used to obtain the tile's URL, including the
      id specifier and any data associated with a transient tile. Again, the
      return value is cached after the first access.
    * The class implements __getitem__() to set the tile id from the traversal
      sub-path, as well as to allow views to be looked up. This is what allows
      a URL like `http://.../@@example.tile/foo` to result in a tile with id
      `foo`.
    """

    __cachedData = None
    __cachedURL = None

    id = None

    def __getitem__(self, name):

        # If we haven't set the id yet, do that first
        if self.id is None:
            self.id = name

            # This is pretty stupid, but it's required to keep the ZPublisher
            # happy in Zope 2. It doesn't normally check for docstrings on
            # views, but it does check for them on sub-objects obtained via
            # __getitem__.

            if self.__doc__ is None:
                self.__doc__ = 'For Zope 2, to keep the ZPublisher happy'

            # Note: X-Tile-Url was added to make it easier for editor to know
            # the URL of a new tile after receiving the redirected response
            # from a tile form. That's why it's only set for customizable tiles
            # (tiles with id).
            if self.id is not None:
                self.request.response.setHeader(
                    'X-Tile-Url',
                    self.url
                )

            return self

        # Also allow views on tiles even without @@.
        viewName = name
        if viewName.startswith('@@'):
            viewName = name[2:]
        view = queryMultiAdapter((self, self.request), name=viewName)
        if view is not None:
            view.__parent__ = self
            view.__name__ = viewName
            return view

        raise KeyError(name)

    def browserDefault(self, request):
        """By default, tiles render themselves with no browser-default view
        """
        return self, ()

    def publishTraverse(self, request, name):
        """Ensure that publish-traversal uses the same semantics as
        __getitem__.
        """
        return self[name]

    def __call__(self, *args, **kwargs):
        if getattr(self, 'index', None) is None:
            raise NotImplemented(
                u'Override __call__ or set a class variable "index" to point '
                u'to a view page template file'
            )
        return self.index(*args, **kwargs)

    @property
    def data(self):
        if self.__cachedData is None:
            reader = ITileDataManager(self)
            self.__cachedData = reader.get()
        return self.__cachedData

    @property
    def url(self):
        return absoluteURL(self, self.request)


@implementer(IPersistentTile)
class PersistentTile(Tile):
    """Base class for persistent tiles. Identical to `Tile`, except that the
    data dict is never serialized with the URL.
    """


class TileThemingTransform(object):
    """Disable plone.app.theming for tile responses"""

    order = 8800

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def transform(self, result, encoding):
        self.request.response.setHeader('X-Theme-Disabled', '1')
        return None

    def transformBytes(self, result, encoding):
        return self.transform(result, encoding)

    def transformUnicode(self, result, encoding):
        return self.transform(result, encoding)

    def transformIterable(self, result, encoding):
        return self.transform(result, encoding)


class TileProtectTransform(object):
    """Replacement transform for plone.protect's ProtectTransform, to drop
    X-Tile-Url-header from unauthorized responses and disable the default
    ProtectTransform for authorized responses (to avoid causing issues
    like extra protect.js-injections for tile editors)
    """

    order = 9000

    def __init__(self, published, request):
        self.published = published
        self.request = request
        try:
            from plone.protect.auto import ProtectTransform
            self.protect = ProtectTransform(published, request)
        except ImportError:
            self.protect = None

    def transform(self, result, encoding):
        from plone.protect import CheckAuthenticator
        CheckAuthenticator(self.request)
        return None

    def transformBytes(self, result, encoding):
        try:
            return self.transform(result, encoding)
        except Forbidden:
            if 'x-tile-url' in self.request.response.headers:
                del self.request.response.headers['x-tile-url']
            if self.protect is not None:
                return self.protect.transformBytes(result, encoding)
            else:
                return None

    def transformUnicode(self, result, encoding):
        try:
            return self.transform(result, encoding)
        except Forbidden:
            if 'x-tile-url' in self.request.response.headers:
                del self.request.response.headers['x-tile-url']
            if self.protect is not None:
                return self.protect.transformUnicode(result, encoding)
            else:
                return None

    def transformIterable(self, result, encoding):
        try:
            return self.transform(result, encoding)
        except Forbidden:
            if 'x-tile-url' in self.request.response.headers:
                del self.request.response.headers['x-tile-url']
            if self.protect is not None:
                return self.protect.transformIterable(result, encoding)
            else:
                return None
