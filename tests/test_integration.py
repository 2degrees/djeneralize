# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011,2013, 2degrees Limited <2degrees-floss@googlegroups.com>.
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

"""Integration tests to confirm nothing Django-related is broken"""

import os
# Ensure that Django knows where the project is:
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_djeneralize.settings'

from django.db.models import Avg, F, Q
from django.db.models.query import ValuesListQuerySet, ValuesQuerySet
from fixture.django_testcase import FixtureTestCase
from nose.tools import (
    eq_, ok_, assert_false, raises, assert_raises, assert_not_equal
    )

from djeneralize.models import BaseGeneralizationModel
from djeneralize.utils import *
from .fixtures import *
from .test_djeneralize.writing.models import *


class TestManager(FixtureTestCase):
    datasets = [PenData, PencilData, FountainPenData, BallPointPenData]


class TestSpecializedQuerySet(FixtureTestCase):
    
    datasets = [PenData, PencilData, FountainPenData, BallPointPenData]
    
    def _check_attributes(self, normal_objects, specialized_objects):
        """
        Helper test to run through the two querysets and test various attributes
        
        """
        
        for normal_object, specialized_object in zip(
            normal_objects, specialized_objects
            ):
            
            eq_(normal_object.pk, specialized_object.pk)
            eq_(normal_object.name, specialized_object.name)
            eq_(normal_object.length, specialized_object.length)
            eq_(normal_object.__class__, WritingImplement)
            assert_not_equal(specialized_object.__class__, WritingImplement)
            ok_(isinstance(specialized_object, WritingImplement))
            assert_not_equal(normal_object, specialized_object)
        
    
    def test_all(self):
        """Check the all() method works correctly"""
        
        all_objects = WritingImplement.objects.all()
        
        all_specializations = WritingImplement.specializations.all()
        
        eq_(len(all_objects), len(all_specializations))
        
        self._check_attributes(all_objects, all_specializations)
    
    def test_filter(self):
        """Check the filter() method works correctly"""
        
        filtered_objects = WritingImplement.objects.filter(length__gte=10)\
                                                   .filter(name__endswith='pen')
                                                   
        filtered_specializations = WritingImplement.specializations\
                                                   .filter(name__endswith='pen')\
                                                   .filter(length__gte=10)
        
        self._check_attributes(filtered_objects, filtered_specializations)
            
        single_filter = WritingImplement.specializations.filter(
            name__endswith='pen', length__gte=10
            )
        
        eq_(single_filter[0], filtered_specializations[0])
    
    def test_exclude(self):
        """Check the exclude() method works correctly"""
        
        excluded_objects = WritingImplement.objects.exclude(length__lt=9)
        excluded_specializations = WritingImplement.specializations.exclude(length__lt=9)
        
        self._check_attributes(excluded_objects, excluded_specializations)
        
    def test_slice_index(self):
        """Check that querysets can be sliced by a single index value correctly"""
        
        all_objects = WritingImplement.objects.all()
        all_specializations = WritingImplement.specializations.all()
        
        eq_(len(all_objects), len(all_specializations))
        
        for i in xrange(len(all_objects)):
            o = all_objects[i]
            s = all_specializations[i]
            
            eq_(o.pk, s.pk)
            eq_(o.name, s.name)
            eq_(o.length, s.length)
            assert_not_equal(o, s)
    
    def test_slice_range(self):
        """Test various range slices for compatibility"""
        
        # Two numbers:
        sliced_objects = WritingImplement.objects.all()[1:4]
        sliced_specializations = WritingImplement.specializations.all()[1:4]
        
        self._check_attributes(sliced_objects, sliced_specializations)
        
        # Just end point:
        sliced_objects = WritingImplement.objects.order_by('length')[:3]
        sliced_specializations = WritingImplement.specializations.order_by('length')[:3]
        
        self._check_attributes(sliced_objects, sliced_specializations)
        
        # Just start point:
        sliced_objects = WritingImplement.objects.order_by('-length')[1:]
        sliced_specializations = WritingImplement.specializations.order_by('-length')[1:]
        
        self._check_attributes(sliced_objects, sliced_specializations)
        
    
    def test_order(self):
        """Test various orderings for compatibility"""
        
        # By name:
        ordered_objects = WritingImplement.objects.order_by('name')
        ordered_specializations = WritingImplement.specializations.order_by('name')
        
        self._check_attributes(ordered_objects, ordered_specializations)
        
        # By inverse length and then name:
        ordered_objects = WritingImplement.objects.order_by('-length', 'name')
        ordered_specializations = WritingImplement.specializations.order_by(
            '-length', 'name'
            )
        
        self._check_attributes(ordered_objects, ordered_specializations)
    
    def test_get(self):
        """Check that the get() method behaves correctly"""
        
        general = WritingImplement.objects.get(name=PenData.GeneralPen.name)
        specialized = WritingImplement.specializations.get(
            name=PenData.GeneralPen.name
            )
        
        self._check_attributes([general], [specialized])
    
    def test_values(self):
        """Check values returns a ValuesQuerySet in both cases"""
        
        normal_values = WritingImplement.objects.values('pk', 'name')
        specialized_values = WritingImplement.specializations.values('pk', 'name')
        
        ok_(isinstance(normal_values, ValuesQuerySet))
        ok_(isinstance(specialized_values, ValuesQuerySet))
        
        for normal_item, specialized_item in zip(
            normal_values, specialized_values
            ):
            
            eq_(normal_item['name'], specialized_item['name'])
            eq_(normal_item['pk'], specialized_item['pk'])
            
    
    def test_values_list(self):
        """Check values_list returns a ValuesListQuerySet in both cases"""
        
        normal_values = WritingImplement.objects.values_list('pk', 'length')
        specialized_values = WritingImplement.specializations.values_list(
            'pk', 'length'
            )
        
        ok_(isinstance(normal_values, ValuesListQuerySet))
        ok_(isinstance(specialized_values, ValuesListQuerySet))
        
        for (n_pk, n_length), (s_pk, s_length) in zip(
            normal_values, specialized_values
            ):
            
            eq_(n_pk, s_pk)
            eq_(n_length, s_length)
            
    def test_flat_values_list(self):
        """
        Check value_list with flat=True  returns a ValuesListQuerySet in both
        cases
        """
        
        normal_values = WritingImplement.objects.values_list('pk', flat=True)
        specialized_values = WritingImplement.specializations.values_list(
            'pk', flat=True
            )
        
        ok_(isinstance(normal_values, ValuesListQuerySet))
        ok_(isinstance(specialized_values, ValuesListQuerySet))
        
        eq_(list(normal_values), list(specialized_values))
    
    def test_aggregate(self):
        """Aggregations work on both types of querysets in the same manner"""
        
        normal_agg = WritingImplement.objects.aggregate(Avg('length'))
        
        specialized_agg = WritingImplement.specializations.aggregate(Avg('length'))
        
        eq_(normal_agg[normal_agg.keys()[0]],
            specialized_agg[specialized_agg.keys()[0]]
            )
    
    def test_count(self):
        """Counts work over both types of querysets"""
        
        normal_count = WritingImplement.objects.filter(length__lt=13).count()
        specialized_count = WritingImplement.objects.filter(length__lt=13).count()
        
        eq_(normal_count, specialized_count)
    
    def test_in_bulk(self):
        """In bulk works across both types of queryset"""
        
        ids = list(WritingImplement.objects.values_list('pk', flat=True))[2:]
        
        normal_bulk = WritingImplement.objects.in_bulk(ids)
        specialized_bulk = WritingImplement.specializations.in_bulk(ids)
        
        eq_(normal_bulk.keys(), specialized_bulk.keys())
        
        self._check_attributes(normal_bulk.values(), specialized_bulk.values())
    
    def test_update(self):
        """update() works the same across querysets"""
        
        original_lengths = list(
            WritingImplement.objects.order_by('length').values_list(
                'length', flat=True
                )
            )
        
        WritingImplement.specializations.all().update(length=1+F('length'))
        
        new_lengths = list(
            WritingImplement.objects.order_by('length').values_list(
                'length', flat=True
                )
            )
        
        for original_length, new_length in zip(original_lengths, new_lengths):
            eq_(original_length+1, new_length)
            
    def test_complex_query(self):
        """SpecializedQuerysets can be constructed from Q objects"""
        
        q_small = Q(length__lt=10)
        q_large = Q(length__gt=13)
        
        normal_objects = WritingImplement.objects.filter(q_small | q_large)
        specialized_objects = WritingImplement.specializations.filter(
            q_small | q_large
            )
        
        self._check_attributes(normal_objects, specialized_objects)