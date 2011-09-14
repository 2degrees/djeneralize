===========================
Querying specialized models
===========================

.. topic:: Overview

	:mod:`djeneralize` allows all the standard Django queries to return
	specialized models instead of the generalized models.
	
The specializations manager
===========================

All models which dervie from :class:`~djeneralize.models.BaseGeneralizationModel`
have a manager ``specializations`` attached to them. This manager works in an
analogous manner to the ``objects`` default manager for Django models, but
instead of returning a :class:`~django.db.models.query.QuerySet`, it returns
a :class:`~djeneralize.query.SpecializedQuerySet`. Iterating over this queryset
gives specialized models instances rather than generalized model instances.

The :class:`~djeneralize.query.SpecializedQuerySet` is like a normal Django
:class:`~django.db.models.query.QuerySet` in that it is lazy and caches the
results of previous lookups, etc. In addition, the
:class:`~djeneralize.query.SpecializedQuerySet` will perform all the relevant
database queries as necessary to retrieve the specific information while, at the
same time ensures that all specializations are retrieved in one go to avoid
hitting the database as little as possible.

all()
-----

The :meth:`all` behaves the same that of a normal queryset, i.e. *all* objects
in the database are returned, expect that they are as their specialized model 
instances::

	>>> qs = WritingImplement.specializations.all()
	>>> type(qs)
	<class 'djeneralize.query.SpecializedQuerySet'>
	>>> qs
	[<FountainPen: Fountain pen>, <Pen: General pen>, <BallPointPen: Ballpoint pen>, <Pencil: Pencil>]
	
filter()
--------

Filter allows filtering of data and can be chained, outputting the specialized
model instances::

	>>> qs1 = WritingImplement.specializations.filter(length__gte=10)
	>>> type(qs1)
	<class 'djeneralize.query.SpecializedQuerySet'>
	>>> qs1
	[<FountainPen: Fountain pen>, <Pen: General pen>, <Pencil: Pencil>]
	>>> qs2 = qs1.filter(name__endswith='pen')
	>>> type(qs2)
	<class 'djeneralize.query.SpecializedQuerySet'>
	>>> qs2
	[<FountainPen: Fountain pen>, <Pen: General pen>]

.. note:: The :meth:`filter` can only take keyword arguments from the general
	model and not from the specialized models as they are meaningless in the
	general context.

extra()
-------

All the functionality in this method is honoured, but only the ``select``
argument is copied over to the cloned
:class:`~djeneralize.query.SpecializedQuerySet`::

    >>> WritingImplement.specializations.extra(select={'description': 'SELECT "The " || name || " is " || length'}).values_list('description', flat=True)
    [u'The Crayola is 5', u'The Bic is 3']

get()
-----

Get allows a single specialized model instance to be retrieved from the database::

	>>> WritingImplement.specializations.get(length=9)
	<BallPointPen: Ballpoint pen>
	
.. note:: This query needs to perform two hits on the database. Firstly to
	ascertain exact specialization to use and secondly to get the specialized
	model instance.	However, if you pass ``specialization_type`` into the lookup
	this will bypass the first-lookup.

final() and direct()
--------------------

As mentioned in :doc:`terminology`, there are two types of specializations
available, the *final* and *direct* specialization. By default,
:class:`~djeneralize.query.SpecializedQuerySet` uses the final specialization
mode of operation. This can also be set by calling
:meth:`~djeneralize.query.SpecializedQuerySet.final`. Conversely, if we want to
swtich to returning direct specializations, we simply call
:meth:`~djeneralize.query.SpecializedQuerySet.direct`. Both of these method
return the updated queryset::

	>>> WritingImplement.specializations.all() # by default, we get final
	[<FountainPen: Fountain pen>, <Pen: General pen>, <BallPointPen: Ballpoint pen>, <Pencil: Pencil>]
	>>> direct = WritingImplement.specializations.direct()
	>>> direct
	[<Pen: Fountain pen>, <Pen: General pen>, <Pen: Ballpoint pen>, <Pencil: Pencil>]
	>>> final = direct.final()
	>>> final
	[<FountainPen: Fountain pen>, <Pen: General pen>, <BallPointPen: Ballpoint pen>, <Pencil: Pencil>]
	
annotate() and raw()
--------------------

Unfortunately, due to the complexities of how the above work is performed on the
underlying SQL query instance, it is not trivial to copy these annotations over
to the specialized model instances and therefore it is not implemented in this
release. It is hoped that the necessary work can be carried out in the future.

For the moment, ``NotImplementedError`` is raised when trying to access annotate
as otherwise misleading result could arise::

	>>> WritingImplement.specializations.annotate()
	------------------------------------------------------------
	Traceback (most recent call last):
	  File "<ipython console>", line 1, in <module>
	  File "/home/euan/.virtualenvs/djeneralize/lib/python2.6/site-packages/Django-1.2.4-py2.6.egg/django/db/models/manager.py", line 147, in annotate
	    return self.get_query_set().annotate(*args, **kwargs)
	  File "/home/euan/dev/git/djeneralize/djeneralize/query.py", line 94, in annotate
	    " to the specialized instances" % self.__class__.__name__
	NotImplementedError: SpecializedQuerySet does not support annotations as these cannot be reliably copied to the specialized instances

and the rest...
---------------

All the other methods and queryset are supported as if you were querying objects.
Any method which returns model instances will always return the specialized
model instances and the others will behave as they do on
:class:`~django.db.models.query.QuerySet`.

Converting a general case model instance into a specialized model instance
==========================================================================

As well as being able to retrieve specialized model instances directly from
queries, it is possible to convert general model instances to their specialized
form via the
:meth:`djeneralize.models.BaseGeneralizedModel.get_as_specialization`. This
takes one keyword argument ``final_specialization`` which is ``True`` by default.
The concept of final and direct is mirrored from the `final() and direct()`_
section above::

	>>> wi = WritingImplement.objects.get(name='Fountain pen')
	>>> wi.get_as_specialization() # gets the final specialization by default
	<FountainPen: Fountain pen>
	>>> wi.get_as_specialization(final_specialization=False)
	<Pen: Fountain pen>
	>>> wi.get_as_specialization(final_specialization=True)
	<FountainPen: Fountain pen>
	