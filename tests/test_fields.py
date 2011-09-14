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
import os
# Ensure that Django knows where the project is:
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_djeneralize.settings'

from fixture.django_testcase import FixtureTestCase
from nose.tools import eq_

from tests.fixtures import BananaData, EcoProducerData, PenData, ShopData
from tests.test_djeneralize.fruit.models import Banana
from tests.test_djeneralize.producers.models import EcoProducer, Shop
from tests.test_djeneralize.writing.models import WritingImplement


class TestForeignKey(FixtureTestCase):
    
    datasets = [EcoProducerData, BananaData, PenData, ShopData]
    
    def test_specialized_foreign_key(self):
        """A SpecializedForeignKey field return the specialized counterpart"""
        eco = EcoProducer.objects.get(name=EcoProducerData.BananaProducer.name)
        eq_(eco.produce.__class__, Banana)
        eq_(eco.pen.__class__, WritingImplement)
    
    def test_specialized_related_manager(self):
        """
        The default specialization manager is used for related object lookups
        
        """
        eco = EcoProducer.objects.get(name=EcoProducerData.BananaProducer.name)
        
        banana = Banana.objects.get(name=BananaData.Banana.name)
        related_object = banana.fruitproducer_set.all()[0]

        eq_(eco, related_object)
    
    def test_non_specialized_related_manager(self):
        """
        SpecializedForeignKey handles vanilla Django model sub-classes as well
        
        """
        
        eco = EcoProducer.objects.get(name=EcoProducerData.BananaProducer.name)
        shop = Shop.objects.get(name=ShopData.EcoMart.name)
        
        related_object = eco.shops.all()[0]
        eq_(shop, related_object)        
