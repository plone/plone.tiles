Changelog
=========

1.2 (2012-11-07)
----------------

- adding icon property for tiletype
  [garbas]

- url that we pass via X-Tile-Url should be relative to current context
  [garbas]

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
