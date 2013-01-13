Changelog
=========

1.0.1 (2013-01-13)
------------------

1.0 - 2011-05-13
----------------

- Release 1.0 Final
  [esteele]

- Add MANIFEST.in.
  [WouterVH]


1.0b5 - 2011-04-06
------------------

- Make RecordsProxy type customizable through ``factory`` argument to
  ``forInterface`` and ``collectionOfInterface``.
  [elro]

- Add ``collectionOfInterface`` support to registry.
  [elro]

- Fixed bug where prefix was ignored by registry.forInterface.
  [elro]

- Add optional min, max arguments for keys/values/items of _Records.
  [elro]


1.0b4 - 2011-02-04
------------------

- Added support for field references, via the ``FieldRef`` class. See
  ``registry.txt`` for details.
  [optilude]

- Change the internal persistent structure around to make it more efficient.
  The API remains the same. Old registries will be migrated when first
  accessed. Warning: This may lead to a "write-on-read" situation for the
  first request in which the registry is being used.
  [optilude]


1.0b3 - 2011-01-03
------------------

 - Added prefix option to forInterface (as it was added to registerInterface)
   [garbas]


1.0b2 - 2010-04-21
------------------

- Added support for Decimal fields
  [optilude]

- Add a prefix option to registerInterface to allow an interface to be used as
  a template for a series of values, rather than single use.
  [MatthewWilkes]


1.0b1 - 2009-08-02
------------------

- Fix a bug in bind() for Choice fields.
  [optilude]


1.0a2 - 2009-07-12
------------------

- Changed API methods and arguments to mixedCase to be more consistent with
  the rest of Zope. This is a non-backwards-compatible change. Our profuse
  apologies, but it's now or never. :-/

  If you find that you get import errors or unknown keyword arguments in your
  code, please change names from foo_bar too fooBar, e.g. for_interface() 
  becomes forInterface().
  [optilude]


1.0a1 - 2009-04-17
------------------

- Initial release
