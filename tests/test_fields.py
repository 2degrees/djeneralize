##############################################################################
#
# Copyright (c) 2011-2016, 2degrees Limited <2degrees-floss@googlegroups.com>.
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
from fixture.django_testcase import FixtureTestCase
from nose.tools import eq_

from tests.fixtures import BananaData
from tests.fixtures import EcoProducerData
from tests.fixtures import PenData
from tests.fixtures import ShopData
from tests.test_djeneralize.fruit.models import Banana
from tests.test_djeneralize.producers.models import EcoProducer
from tests.test_djeneralize.writing.models import WritingImplement


class TestForeignKey(FixtureTestCase):

    datasets = [EcoProducerData, BananaData, PenData, ShopData]

    def test_specialized_foreign_key(self):
        """A SpecializedForeignKey field return the specialized counterpart"""
        eco = EcoProducer.objects.get(name=EcoProducerData.BananaProducer.name)
        eq_(eco.produce.__class__, Banana)
        eq_(eco.pen.__class__, WritingImplement)
