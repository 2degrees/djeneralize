# -*- coding: utf-8 -*-
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
"""Test suite to ensure that correct copying of managers"""

from django.db.models.manager import Manager
from nose.tools import eq_
from nose.tools import ok_

from djeneralize.manager import SpecializationManager
from tests.test_djeneralize.fruit.models import Apple
from tests.test_djeneralize.fruit.models import Banana
from tests.test_djeneralize.fruit.models import Fruit
from tests.test_djeneralize.fruit.models import FruitManager
from tests.test_djeneralize.fruit.models import SpecializedFruitManager


class TestManager(object):

    def test_correct_manager_declared(self):
        """
        The specializations attribute of Fruit points to SpecializedFruitManager
        and not SpecializationManager.

        """

        ok_(isinstance(Fruit.specializations, SpecializedFruitManager),
            "Expected Fruit.specializations to be an instance of "
            "SpecializedFruitManager, but got %s" %
            Fruit.specializations.__class__
            )

    def test_default_manager(self):
        """The _default_manager isn't perturbed by djeneralize"""

        ok_(isinstance(Fruit._default_manager, FruitManager))

    def test_base_manager(self):
        """The _default_manager isn't perturbed by djeneralize"""

        ok_(isinstance(Fruit._base_manager, Manager))

    def test_default_specialization_manager_set(self):
        """
        The _default_specialization_manager should always be set on
        BaseGeneralizationModel sub-classes

        """

        ok_(hasattr(Fruit, '_default_specialization_manager'))
        ok_(isinstance(
            Fruit._default_specialization_manager, SpecializedFruitManager
            ), 'Expected Fruit._default_specialization_manager to be an '
            'instance of SpecializedFruitManager, but found %s' %
            Fruit._default_specialization_manager.__class__
            )

    def test_base_specialization_manager_set(self):
        """
        The _base_specialization_manager should always be set on
        BaseGeneralizationModel sub-classes

        """

        ok_(hasattr(Fruit, '_base_specialization_manager'))
        eq_(Fruit._base_specialization_manager.__class__, SpecializationManager)

    def test_specialized_not_inherit_specialized_managers(self):
        """
        Like normal managers, Specialized models do not copy the managers from
        their parent.

        """

        eq_(Apple.specializations.__class__, SpecializationManager)
        eq_(Banana.specializations.__class__, SpecializationManager)
