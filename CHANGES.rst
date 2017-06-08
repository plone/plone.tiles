Changelog
=========

1.8.3 (2017-06-08)
------------------

Bug fixes:

- Do not swallow ``AttributeError`` inside ``index()`` on template rendering.
  [hvelarde]


1.8.2 (2017-01-10)
------------------

Bug fixes:

- Fix issue where transient tile was unable to encode data
  with list of unicode strings
  [datakurre]

- Remove unused unittest2 requirement
  [tomgross]


1.8.1 (2016-11-24)
------------------

Bugfix:

- Fix encode error in nested unicodes (like in plone.app.querystring)
  [tomgross]

- Restructure testing
  [tomgross]


1.8.0 (2016-09-13)
------------------

New features:

  - Provide ignore_querystring form directive to mark particular tiles fields
    that are not allowed to default data from query string data
    [vangheem]


1.7.1 (2016-09-12)
------------------

- Fix issue where collective.cover was broken, because internal changes in
  default data managers
  [datakurre]

1.7.0 (2016-09-08)
------------------

New features:

- Option to customize storage layer with ITileDataStorage adapter
  [datakurre]


1.6.1 (2016-09-07)
------------------

Bug fixes:

- Reformat docs.
  [gforcada]

- Add coveralls shield.
  [gforcada]


1.6 (2016-06-27)
----------------

- Let TileType instances (tile registration utility) know about the view
  permission too.
  [jensens]


1.5.2 (2016-03-28)
------------------

- Fix issue where ESI href was not properly replaced.
  [jensens]

- Add section "ZCML Reference" to README.rst.
  [jensens]

- PEP8, code-analysis, documentation and packaging fixes.
  [jensens, mauritsvanrees]


1.5.1 (2015-10-09)
------------------

- Fix decoding List type of Choice value types
  [vangheem]


1.5.0 (2015-09-04)
------------------

- Add support for overriding transient data manager with persistent data
  manager by adding X-Tile-Persistent=1 into tile URL
  [datakurre]

- Fix persistent data manager to read its default from query string
  [vangheem]

1.4.0 (2015-05-25)
------------------

- Add support for encoding dictionary fields into tile URL
  [datakurre]
- Fix issue where saving or deleting transient tile data mutated the current request
  [datakurre]
- Fix issue where non-ascii characters in tile data raised UnicodeEncode/DecodeErrors
  [datakurre]

1.3.0 (2015-04-21)
------------------

- Fix edit_permission and delete_permission to default
  to add_permission only in TileType constructor
  [datakurre]

- Fix argument order in TileType constructor call
  [datakurre]

- Fix absolute_url-adapter to fallback to relative URL
  [datakurre]

- Add response to include absolute X-Tile-Url header
  [bloodbare]

1.2 (2012-11-07)
----------------

- Adding icon property for tiletype
  [garbas]

- Url that we pass via X-Tile-Url should be relative to current context
  [garbas]

- Adding support for more robust permissions for edit and delete on tiles
  [cewing calvinhp]

1.1 (2012-06-22)
----------------

- X-Tile-Uid header is passed on tile view containing tile's id.
  [garbas]

- PEP 8/Pyflakes (ignoring E121, E123, E126, E127 and E501).
  [hvelarde]

1.0 (2012-05-14)
----------------

- Refactor ESI support. To use the ``ESITile`` and ``ESIPersistentTile``
  base classes, you should either use a template assigned via ZCML or
  override the ``render()`` method. See ``esi.rst`` for full details.
  [optilude]

- Internationalized title and description of the tile directive.
  [vincentfretin]

- Use a  json-encoded parameter in transient tiles as first option.
  [dukebody]

- Use adapters for the Zope Publisher type casting
  [dukebody]

- Conditionaly support z3c.relationfield's RelationChoice fields
  [dukebody]

- Ignore type casting for fields without fixed type, like zope.schema.Choice
  [dukebody]

1.0a1 (2010-05-17)
------------------

- Initial release.
