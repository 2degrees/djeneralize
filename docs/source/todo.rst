=========
TODO list
=========

.. topic:: Overview
	
	Although :mod:`djeneralize` is performing all the goals it set out to do in
	our specification, development has revealed several areas which are missing
	in terms of replicating everything Django's queryset does. Ideally we will
	aim to reflect all of this functionality eventually.
	
Add annotations
===============

It would be nice that any annotations from the parent queryset could be copied
over to the ``in_bulk`` call to generate the specializations. The way Django
handles annotations is not trivial and quite a bit of time and effort will be
needed to be invested to resolve this issue.

Additionally any ``extra()`` and ``raw()`` calls should be supported where
possible.

Deferred loading of fields
==========================

This seems like it should be working correctly, but there seems to be a
deficiency here. I'm not sure whether there is a bug in Django with inherited
tables as this doesn't seem to be working correctly on the ``objects`` queryset
either.

Copy managers correctly
=======================

At present any sub-classes of the
:class:`~djeneralize.manager.SpecializationManager` added to a general case
model will not be copied and re-instantiated on child models. There is a bit of
extra work to do here as it's important to ensure that the ``_meta`` attribute
of specialized models can cope with the extra fields of
:attr:`_default_specialization_manager` and :attr:`_base_specialization_manager`.