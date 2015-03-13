"""Test suite to ensure that correct copying of managers"""

import os
# Ensure that Django knows where the project is:
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_djeneralize.settings'

from django.db.models.manager import Manager
from fixture.django_testcase import FixtureTestCase
from nose.tools import (
    eq_, ok_, assert_false, raises, assert_raises, assert_not_equal
    )

from djeneralize.manager import SpecializationManager
from .test_djeneralize.fruit.models import *


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
