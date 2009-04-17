============
Introduction
============

This package provides debconf-like (or about:config-like) settings registries
for Zope applications. A `registry`, with a dict-like API, is used to get and
set values stored in `records`. Each record contains the actual value, as
well as a `field` that describes the record in more detail. At a minimum, the
field contains information about the type of value allowed, as well as a short
title describing the record's purpose.

See the following doctests for more details: 

 * `registry.txt`, which demonstrates how registries and records work
 * `events.txt`, which shows the events that are fired from the registry
 * `field.txt`, which describes the behaviour of persistent fields

