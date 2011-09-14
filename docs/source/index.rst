=======================================
Welcome to djeneralize's documentation!
=======================================

Overview
========

The aim of djeneralize is to enhance Django's model-inheritance and allow the
user to declare specializations of a general case model and then query the
generalized model, but returns instances of the specialized model, e.g.::

	>>> Fruit.objects.all()
	[<Fruit: Rosy apple>, <Fruit: Bendy banana>, <Fruit: Sweet clementine>]
	>>> Fruit.specializations.all()
	[<Apple: Rosy apple>, <Banana: Bendy banana>, <Clementine: Sweet clementine>]
	

Contents
========

.. toctree::
   :maxdepth: 2
   
   terminology
   introduction
   defining_models
   querying
   api
   todo

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

