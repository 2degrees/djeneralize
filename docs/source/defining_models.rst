=====================================
Defining models with specializations
=====================================

.. topic:: Overview
	
	This document describes the customizations you will need to make to your
	Django models to make the specialization code work. There's not too much to
	bear in mind, so the switch should be easy!
	
Example models
==============

Let us consider the models we defined in :doc:`introduction`:

.. literalinclude:: example_models.py

Derive your model from :class:`~djeneralize.models.BaseGeneralizationModel`
===========================================================================

The top-level model is derived from :class:`djeneralize.models.BaseGeneralizationModel`
and not :class:`django.db.models.Model`. Just make sure this class is
imported at the top of the module and that's the inheritance done!
 
Set up the specialization for your models
=========================================

You must explicitly declare the specialization that your model exhibits. In most
cases the naming can be similar to the class name, but only alphanumeric
characters are accepted here.

This declaration should always be done in the inner ``class Meta`` declaration.

.. note:: The top-most sub-class of BaseGeneralizedModel does not require and,
	in fact, forbids the declaration of a specialization.
	
These specializations are used by :mod:`djeneralize` to keep track of the
relationships between the general case and the specializations. The model
calculates a "path" for each specialization with the most general case being
assigned the ``/`` path. This value is stored on the specialization_type field,
so be careful when altering this field.

.. warning:: If the inheritance scheme changes for your models you will need to
	create a database migration to ensure that the ``specialization_type`` field
	is correctly mapped to the new structure of your inheritance.