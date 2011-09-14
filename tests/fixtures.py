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
from tests.test_djeneralize.producers.models import EcoProducer
from tests.test_djeneralize.fruit.models import Banana

"""Fixtures for djeneralize tests"""

from decimal import Decimal as D

from fixture import DataSet


__all__ = [
    'PenData', 'FountainPenData', 'BallPointPenData', 'PencilData',
    'EcoProducerData',
    ]


class PenData(DataSet):
    
    class Meta:
        django_model = 'writing.Pen'
    
    class GeneralPen:
        specialization_type = '/pen/'
        name = 'General pen'
        length = 15
        ink_colour = 'Blue'
        

class FountainPenData(DataSet):
    
    class Meta:
        django_model = 'writing.FountainPen'
    
    class MontBlanc:
        specialization_type = '/pen/fountain_pen/'
        name = 'Mont Blanc'
        length = 18
        ink_colour = 'Black'
        nib_width = D('1.25')
        
    class Parker:
        specialization_type = '/pen/fountain_pen/'
        name = 'Parker'
        length = 14
        ink_colour = 'Blue'
        nib_width = D('0.75')

class BallPointPenData(DataSet):
    
    class Meta:
        django_model = 'writing.BallPointPen'
    
    class Bic:
        specialization_type = '/pen/ballpoint_pen/'
        name = 'Bic'
        length = 12
        ink_colour = 'Blue'
        replaceable_insert = False
        
    class Papermate:
        specialization_type = '/pen/ballpoint_pen/'
        name = 'Papermate'
        length = 13
        ink_colour = 'Green'
        replaceable_insert = True
        
        
class PencilData(DataSet):
    
    class Meta:
        django_model = 'writing.Pencil'
    
    class Crayola:
        specialization_type = '/pencil/'
        name = 'Crayola'
        length = 8
        lead = 'B2'
        
    class Technical:
        specialization_type = '/pencil/'
        name = 'Technical'
        length = 12
        lead = 'H5'


class BananaData(DataSet):
    
    class Meta:
        django_model = 'fruit.Banana'
    
    class Banana:
        specialization_type = Banana.model_specialization
        name = 'Banana from Canary Islands'
        curvature = D('1.10')
    

class EcoProducerData(DataSet):
    
    class Meta:
        django_model = 'producers.EcoProducer'
    
    class BananaProducer:
        specialization_type = EcoProducer.model_specialization
        name = 'Ecological Producer'
        produce = BananaData.Banana
        pen = PenData.GeneralPen
        fertilizer = 'Love'
