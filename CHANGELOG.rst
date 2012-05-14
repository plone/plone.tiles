Changelog
=========

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
