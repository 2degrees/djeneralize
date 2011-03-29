# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011, 2degrees Limited <egoddard@tech.2degreesnetwork.com>.
# All Rights Reserved.
#
# This file is part of djeneralize <https://github.com/2degrees/djeneralize>,
# which is subject to the provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

from itertools import chain
import os
# Ensure that Django knows where the project is:
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_djeneralize.settings'

from django.http import Http404
from fixture.django_testcase import FixtureTestCase
from nose.tools import (
    eq_, ok_, assert_false, raises, assert_raises, assert_not_equal
    )

from djeneralize.models import BaseGeneralizationModel
from djeneralize.utils import *
from .fixtures import *
from .test_djeneralize.writing.models import *


class TestMetaclass(object):
    """Tests for the actions the metaclass performs"""
    
    
    def test_specializations_general(self):
        """
        The specializations dictionary on the most general case is populated
        with all the descdencts direct or otherwise.
        
        """
        
        specializations = WritingImplement._meta.specializations
        specializations_classes = set(specializations.values())
        specializations_keys = set(specializations.keys())
        
        ok_(Pen in specializations_classes)
        ok_(Pencil in specializations_classes)
        ok_(FountainPen in specializations_classes)
        ok_(BallPointPen in specializations_classes)
        
        ok_(Pen.model_specialization in specializations_keys)
        ok_(Pencil.model_specialization in specializations_keys)
        ok_(FountainPen.model_specialization in specializations_keys)
        ok_(BallPointPen.model_specialization in specializations_keys)
        
    
    def test_sub_specialization(self):
        """
        Only the child specializations are stored in a specialization of the
        general case.
        
        """
        
        specializations = Pen._meta.specializations
        specializations_classes = set(specializations.values())
        specializations_keys = set(specializations.keys())
        
        assert_false(Pen in specializations_classes)
        assert_false(Pencil in specializations_classes)
        ok_(FountainPen in specializations_classes)
        ok_(BallPointPen in specializations_classes)
        
        assert_false(Pen.model_specialization in specializations_keys)
        assert_false(Pencil.model_specialization in specializations_keys)
        ok_(FountainPen.model_specialization in specializations_keys)
        ok_(BallPointPen.model_specialization in specializations_keys)
        
        eq_(BallPointPen._meta.specializations, {})
        
    def test_path_specialization(self):
        """
        The specialization for each (sub-)class of the generalized model has it
        ancestry recorded.
        
        """
        
        eq_(WritingImplement.model_specialization, '/')
        eq_(Pen.model_specialization, '/pen/')
        eq_(Pencil.model_specialization, '/pencil/')
        eq_(FountainPen.model_specialization, '/pen/fountain_pen/')
        eq_(BallPointPen.model_specialization, '/pen/ballpoint_pen/')
        
    @raises(TypeError)
    def test_missing_meta(self):
        """All specializations must declare a inner class Meta"""
        
        no_meta_factory()
        
    @raises(TypeError)
    def test_missing_specialization(self):
        """
        All specializations must declare a inner class Meta which defines their
        specialization.
        
        """
        
        no_specialization_factory()
    
    @raises(ValueError)
    def test_invalid_specialization(self):
        """
        All declared specializations must contain only alphanumeric characters.
        
        """
        
        invalid_specialization_factory()
        
    @raises(TypeError)
    def test_abstract_specializations(self):
        """
        It is not permissible to declare specializations if the model is
        abstract.
        
        """
        
        abstract_specialization_factory()
        
    @raises(TypeError)
    def test_general_specializations(self):
        """
        It is not permissible to declare specializations if the model is
        a direct sub-class of BaseGeneralizationModel.
        
        """
        
        base_generalization_with_specialization_factory()
        
        
class TestFindNextPathDown(object):
    """Tests for find_next_path_down."""
    
    def test_root_down(self):
        """Test the path below the root path can be identified correctly."""
        
        root = '/'
        full_path = '/home/barry/dev/'
        
        eq_(find_next_path_down(root, full_path, '/'), '/home/')
        
    def test_non_root(self):
        """Test the path below a non-root path can be identified correctly"""
        
        non_root = '/home/'
        full_path = '/home/barry/dev/'
        
        eq_(find_next_path_down(non_root, full_path, '/'), '/home/barry/')    


class TestDefaultSpecialization(FixtureTestCase):
    """
    Test for automatic setting of the default specialization type at creation
    time on BaseGeneralizedModel
    
    """
    
    def test_match(self):
        """
        Ensure that the default specialization type is set correctly
        
        """
        pencil = FountainPen()
        eq_(pencil.specialization_type, FountainPen.model_specialization)


class TestGetAsSpecialization(FixtureTestCase):
    """Tests for the get_as_specialization method on general models"""
    
    datasets = [PenData, PencilData, FountainPenData, BallPointPenData]
    
    def test_no_matching_specialization_raises_key_error(self):
        """
        If get_as_specialization is called on the most specialized instance a
        key error will be raised.
        
        """
        
        pencil = Pencil.objects.all()[0]
        
        assert_raises(KeyError, pencil.get_as_specialization)
        
    def test_final_specialization(self):
        """
        By default the get_as_specialization method returns the most specialized
        specialzation.
        
        """
        
        montblanc_general = WritingImplement.objects.get(name='Mont Blanc')
        montblanc_intermediate = Pen.objects.get(name='Mont Blanc')
        montblanc_special = FountainPen.objects.get(name='Mont Blanc')
        
        eq_(montblanc_general.get_as_specialization(), montblanc_special)
        
        eq_(montblanc_intermediate.get_as_specialization(), montblanc_special)
        
    def test_direct_specialization(self):
        """
        The get_as_specialization method can get the most direct specialization
        by setting final_specialization=False.
        
        """
        
        montblanc_general = WritingImplement.objects.get(name='Mont Blanc')
        montblanc_intermediate = Pen.objects.get(name='Mont Blanc')
        montblanc_special = FountainPen.objects.get(name='Mont Blanc')
        
        eq_(montblanc_general.get_as_specialization(False),
            montblanc_intermediate
            )
        
        eq_(montblanc_intermediate.get_as_specialization(False),
            montblanc_special
            )
        
class TestSpecializedQueryset(FixtureTestCase):
    """
    Tests for the specialized queryset (and therefore for the specialized
    manager as well).
    
    """
    
    datasets = [PenData, PencilData, FountainPenData, BallPointPenData]
    
    def setUp(self):
        # Transform the datasets into a dictionary keyed by name:
        datasets = {}
        
        all_datasets = chain(
            PenData.__dict__.items(), PencilData.__dict__.items(),
            FountainPenData.__dict__.items(), BallPointPenData.__dict__.items()
            )
        
        for class_name, inner_class in all_datasets:
            if class_name.startswith('_') or class_name == 'Meta':
                continue
            
            datasets[inner_class.name] = inner_class
            
        self.datasets = datasets
    
    def test_all_final(self):
        """
        The all() method on the manager and queryset returns final 
        specializations.
        
        """
        
        all_writing_implements = WritingImplement.specializations.all()
        
        models = set(m.__class__ for m in all_writing_implements)
        
        assert_false(WritingImplement in models)
        ok_(Pen in models)
        ok_(Pencil in models)
        ok_(FountainPen in models)
        ok_(BallPointPen in models)
        
        
        # Ensure that all the objects have the correct fields and values
        # specified in their original definition, i.e. they've been
        # reconstituted correctly:
        for wi in all_writing_implements:
            dataset = self.datasets[wi.name]
            
            for field_name, value in dataset.__dict__.items():
                if field_name.startswith('_') or field_name == 'ref':
                    continue
                
                model_value = getattr(wi, field_name)
                eq_(model_value, value)
    
    def test_all_direct(self):
        """
        The all() method on the manager and queryset returns direct 
        specializations for the specializations manager and calling the direct()
        method.
        
        """
        
        all_writing_implements = WritingImplement.specializations.direct().all()
        
        models = set(m.__class__ for m in all_writing_implements)
        
        assert_false(WritingImplement in models)
        ok_(Pen in models)
        ok_(Pencil in models)
        assert_false(FountainPen in models)
        assert_false(BallPointPen in models)
        
    def test_filter_chain_final(self):
        """
        Chained calls to the filter() method on the specialized queryset return
        final specializations
        
        """
        
        filtered_writing_implements = WritingImplement.specializations.filter(
            length__gt=10 # call to the manager
            ).filter(
            specialization_type__startswith='/pen/' # call to the queryset
            )
        
        models = set(m.__class__ for m in filtered_writing_implements)
        
        assert_false(WritingImplement in models)
        ok_(Pen in models)
        assert_false(Pencil in models)
        ok_(FountainPen in models)
        ok_(BallPointPen in models)
        
        expected_names = [
            'General pen', 'Mont Blanc', 'Parker', 'Bic', 'Papermate'
            ]
        
        for expected_name, wi in zip(expected_names, filtered_writing_implements):
            eq_(expected_name, wi.name)
            
    def test_filter_chain_direct(self):
        """
        Chained calls to the filter() method on the specialized queryset return
        direct specializations via the specializations manager and calling the
        direct()
        
        """
        
        filtered_writing_implements = WritingImplement.specializations.filter(
            length__gt=10 # call to the manager
            ).filter(
            specialization_type__startswith='/pen/' # call to the queryset
            ).direct()
        
        models = set(m.__class__ for m in filtered_writing_implements)
        
        assert_false(WritingImplement in models)
        ok_(Pen in models)
        assert_false(Pencil in models)
        assert_false(FountainPen in models)
        assert_false(BallPointPen in models)
        
        expected_names = [
            'General pen', 'Mont Blanc', 'Parker', 'Bic', 'Papermate'
            ]
        
        for expected_name, wi in zip(expected_names, filtered_writing_implements):
            eq_(expected_name, wi.name)
            
    def test_get_final(self):
        """
        Calling get() returns the final specialization when calling the
        specialization manager
        
        """
        
        mont_blanc = WritingImplement.specializations.get(name='Mont Blanc')
        
        eq_(mont_blanc.__class__, FountainPen)
        eq_(mont_blanc.nib_width, FountainPenData.MontBlanc.nib_width)
        eq_(mont_blanc.length, FountainPenData.MontBlanc.length)
        
        mont_blanc = Pen.specializations.get(name='Mont Blanc')
        
        eq_(mont_blanc.__class__, FountainPen)
        
        
    def test_get_direct(self):
        """
        Calling get() returns the direct specialization when calling the
        specialization manager and setting direct()
        
        """
        
        mont_blanc = WritingImplement.specializations.direct().get(
            name='Mont Blanc'
            )
        
        eq_(mont_blanc.__class__, Pen)
        
        mont_blanc = Pen.specializations.direct().get(name='Mont Blanc')
        
        eq_(mont_blanc.__class__, FountainPen)
        
    def test_final(self):
        """
        Calling the final() method on the manager or queryset ensures that the
        _final_specialization is set to True
        
        """
        
        qs = WritingImplement.specializations.final()
        ok_(qs._final_specialization)
        
        qs = WritingImplement.specializations.direct().final()
        ok_(qs._final_specialization)
        
    def test_direct(self):
        """
        Calling the direct() method on the manager or queryset ensures that the
        _final_specialization is set to False
        
        """
        
        qs = WritingImplement.specializations.direct()
        assert_false(qs._final_specialization)
        
        qs = WritingImplement.specializations.final().direct()
        assert_false(qs._final_specialization)
        
    def test_annotate(self):
        """Annotation is not possible for SpecializedQuerySets"""
        
        assert_raises(
            NotImplementedError, WritingImplement.specializations.annotate
            )    
        
    def test_ordering(self):
        """Ordering of the initial queryset is respected in the child objects"""
        
        lengths = sorted(
            WritingImplement.objects.values_list('length', flat=True)
            )
        
        ordered_wi = WritingImplement.specializations.order_by('length')
        
        for wi, expected_length in zip(ordered_wi, lengths):
            assert_not_equal(wi.__class__, WritingImplement)
            eq_(wi.length, expected_length)
            
    def test_slicing_range(self):
        """
        Slicing the queryset with a range gives specialized model instances.
        
        """
        
        ordered_wi = WritingImplement.specializations.order_by('length')[1:3]
        
        first_wi, second_wi = tuple(ordered_wi)
        
        eq_(first_wi, Pencil.objects.get(name='Technical'))
        eq_(second_wi, BallPointPen.objects.get(name='Bic'))
        
    def test_slicing_single_index(self):
        """
        Slicing the queryset with a single value gives a single specialized
        model instance.
        
        """
        
        wi = WritingImplement.specializations.order_by('length')[5]
        
        assert_not_equal(wi.__class__, WritingImplement)
        eq_(wi, Pen.objects.all()[0])
        

class TestGetSpecializationOr404(FixtureTestCase):
    """Tests for get_specialization_or_404"""
    
    datasets = [PenData, PencilData, FountainPenData, BallPointPenData]
    
    def test_model_class_exists(self):
        """
        get_specialization_or_404 returns the specialized model instance if it
        is called with a BaseSpecialized model class and parameters which
        correspond to a DB entry. 
        
        """
        
        pencil = Pencil.objects.get(name=PencilData.Technical.name)
        eq_(pencil, get_specialization_or_404(
            WritingImplement, name=PencilData.Technical.name
            ))
        
    def test_model_class_does_not_exist(self):
        """
        get_specialization_or_404 raises a Http404 error if it is called with a
        BaseSpecialized model class and parameters which do not correspond to a
        DB entry. 
        
        """
        
        assert_raises(
            Http404, get_specialization_or_404, WritingImplement,
            name='some thing else'
            )
        
    def test_manager_exists(self):
        """
        get_specialization_or_404 returns the specialized model instance if it
        is called with a SpecializedManager instance and parameters which
        correspond to a DB entry. 
        
        """
        
        pencil = Pencil.objects.get(name=PencilData.Technical.name)
        eq_(pencil, get_specialization_or_404(
            WritingImplement.specializations, name=PencilData.Technical.name
            ))
        
    def test_manager_does_not_exist(self):
        """
        get_specialization_or_404 raises a Http404 error if it is called with a
        SpecializedManager instance and parameters which do not correspond to a
        DB entry. 
        
        """
        
        assert_raises(
            Http404, get_specialization_or_404, WritingImplement.specializations,
            name='some thing else'
            )
        
    def test_queryset_exists(self):
        """
        get_specialization_or_404 returns the specialized model instance if it
        is called with a SpecializedQuerySet instance and parameters which
        correspond to a DB entry. 
        
        """
        
        pencil = Pencil.objects.get(name=PencilData.Technical.name)
        eq_(pencil, get_specialization_or_404(
            WritingImplement.specializations.all(),
            name=PencilData.Technical.name
            ))
        
    def test_queryset_does_not_exist(self):
        """
        get_specialization_or_404 raises a Http404 error if it is called with a
        SpecializedQuerySet instance and parameters which do not correspond to a
        DB entry. 
        
        """
        
        assert_raises(
            Http404, get_specialization_or_404,
            WritingImplement.specializations.all(), name='some thing else'
            )
    
