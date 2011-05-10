============
Introduction
============

Django supports inherited model declarations through the sub-classing of model
classes in python code. However, the use case for these inherited models is to
only deal with the sub-classes themselves, and not to consider the role of
sub-classes in the context of their super-class. The aim of :mod:`djeneralize`
is to provide a way of mixing specializations of a general model case and work
with both the general case and the special cases interchangeably.

.. note:: Before reading through the examples, it is a good idea to be familiar
	with some of the :doc:`terminology`.

Let us consider the following example of model declarations which are contained
within the ``writing`` app:

.. literalinclude:: example_models.py

What we get from Django
=======================

Django handles the creation of the related tables for these models very nicely.
If we execute ``python manage.py sqlall writing``, we get the following with a
Postgres backend):

.. code-block:: sql

	BEGIN;
	CREATE TABLE "writing_writingimplement" (
	    "id" integer NOT NULL PRIMARY KEY,
	    "specialization_type" text NOT NULL,
	    "name" varchar(30) NOT NULL,
	    "length" integer NOT NULL
	)
	;
	CREATE TABLE "writing_pencil" (
	    "writingimplement_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "writing_writingimplement" ("id"),
	    "lead" varchar(2) NOT NULL
	)
	;
	CREATE TABLE "writing_pen" (
	    "writingimplement_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "writing_writingimplement" ("id"),
	    "ink_colour" varchar(30) NOT NULL
	)
	;
	CREATE TABLE "writing_fountainpen" (
	    "pen_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "writing_pen" ("writingimplement_ptr_id"),
	    "nib_width" decimal NOT NULL
	)
	;
	CREATE TABLE "writing_ballpointpen" (
	    "pen_ptr_id" integer NOT NULL PRIMARY KEY REFERENCES "writing_pen" ("writingimplement_ptr_id"),
	    "replaceable_insert" bool NOT NULL
	)
	;
	CREATE INDEX "writing_writingimplement_524e029a" ON "writing_writingimplement" ("specialization_type");
	COMMIT;

If we inspect the available fields on the general model (``WritingImplement``)
and its sub-classes, we find that Django has set-up all the required fields
respecting the models' inheritance::

	>>> from writing.models import *
	>>> WritingImplement._meta.get_all_field_names()
	['id', 'length', 'name', 'pen', 'pencil', 'specialization_type']
	>>> Pen._meta.get_all_field_names()
	['ballpointpen', 'fountainpen', 'id', 'ink_colour', 'length', 'name', 'specialization_type', 'writingimplement_ptr']
	>>> Pencil._meta.get_all_field_names()
	['id', 'lead', 'length', 'name', 'specialization_type', 'writingimplement_ptr']
	>>> FountainPen._meta.get_all_field_names()
	['id', 'ink_colour', 'length', 'name', 'nib_width', 'pen_ptr', 'specialization_type', 'writingimplement_ptr']
	>>> BallPointPen._meta.get_all_field_names()
	['id', 'ink_colour', 'length', 'name', 'pen_ptr', 'replaceable_insert', 'specialization_type', 'writingimplement_ptr']
	
So far, so good. When we have the general case instances, we get just the general
fields and when we're using specialized model instances, we have all the
specialized fields. However, ...


What djeneralize does to extend Django's functionality
======================================================

This specificity and generality are all well and good, but if we have a
collection of writing implements and want to consider exactly to which sub-classes
of WritingImplement they belong, then we don't get any assistance from Django::

	>>> general_pen = Pen.objects.create(length=10, name='General pen', ink_colour='Black')
	>>> fountain_pen = FountainPen.objects.create(length=15, name='Fountain pen', ink_colour='Blue', nib_width='1.2')  
	>>> ballpoint_pen = BallPointPen.objects.create(length=9, name='Ballpoint pen', ink_colour='Green', replaceable_insert=False)
	>>> pencil = Pencil.objects.create(length=12, name='Pencil', lead='HB')
	>>> WritingImplement.objects.all()
	[<WritingImplement: General pen>, <WritingImplement: Fountain pen>, <WritingImplement: Ballpoint pen>, <WritingImplement: Pencil>]
	>>> Pen.objects.all()
	[<Pen: General pen>, <Pen: Fountain pen>, <Pen: Ballpoint pen>]
	>>> FountainPen.objects.all()
	[<FountainPen: Fountain pen>]
	
These lists are all correct in terms of the model instances which are returned,
but wouldn't it be great if we could query all our writing implements and get
back a queryset which, when iterated over gave us instances of the
specializations. With :mod:`djeneralize` this is a possibility::

	>>> WritingImplement.specializations.all()
	[<FountainPen: Fountain pen>, <Pen: General pen>, <BallPointPen: Ballpoint pen>, <Pencil: Pencil>]
	
Additionally, if we have a general case model instance, we can get its
specialization::

	>>> wi = WritingImplement.objects.get(length=9)
	>>> wi
	<WritingImplement: Ballpoint pen>
	>>> wi.get_as_specialization()
	<BallPointPen: Ballpoint pen>
	
That's about all there is to :mod:`djeneralize`. To make this all work, take a 
look at :doc:`defining_models`.