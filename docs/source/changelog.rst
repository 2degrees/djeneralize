================================
Changelog for :mod:`djeneralize`
================================

Version 1.1
===========

- Added support for :meth:`extra` in :class:`~djeneralize.query.SpecializedQuerySet`.
- Added :class:`~djeneralize.fields.SpecializedForeignKey` to cater for
  referring to related models which are specializations.