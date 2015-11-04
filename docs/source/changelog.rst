================================
Changelog for :mod:`djeneralize`
================================

Version 1.3 Final (unreleased)
==============================

- Added support for Django 1.7.


Version 1.3 Release Candidate 2
===============================

- Added support for Django 1.6.


Version 1.3 Release Candidate 1
===============================

(This release was a mistake)

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