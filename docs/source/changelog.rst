================================
Changelog for :mod:`djeneralize`
================================

Version 1.2 Release Candidate 1
===============================

- Added support for Django 1.5.


Version 1.2 Beta 1
==================

- Added support for Django 1.4.
- Dropped specialization of objects returned by reverse relationships
  of :class:`~djeneralize.fields.SpecializedForeignKey` fields.

Version 1.1
===========

- Added support for :meth:`extra` in :class:`~djeneralize.query.SpecializedQuerySet`.
- Added :class:`~djeneralize.fields.SpecializedForeignKey` to cater for
  referring to related models which are specializations.