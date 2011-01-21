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

from django.db import models

from djeneralize.manager import SpecializationManager
from djeneralize.models import BaseGeneralizationModel

__all__ = [
    'WritingImplement', 'Pencil', 'Pen', 'FountainPen', 'BallPointPen',
    'no_meta_factory', 'no_specialization_factory',
    'invalid_specialization_factory', 'abstract_specialization_factory',
    'base_generalization_with_specialization_factory'
    ]

#{ General model

class WritingImplement(BaseGeneralizationModel):
    name = models.CharField(max_length=30)
    length = models.IntegerField()
    
    def __unicode__(self):
        return self.name

#}

#{ Direct children of WritingImplement, i.e. first specializtion 

class Pencil(WritingImplement):
    
    lead = models.CharField(max_length=2) # i.e. HB, B2, H5
    
    class Meta:
        specialization = 'pencil'
        
class Pen(WritingImplement):
    
    ink_colour = models.CharField(max_length=30)
    
    class Meta:
        specialization = 'pen'

#}
    
#{ Grand-children of WritingImplement, i.e. second degree of specialization

class FountainPen(Pen):
    
    nib_width = models.DecimalField(max_digits=3, decimal_places=2)
    
    class Meta:
        specialization = 'fountain_pen'
        
        
class BallPointPen(Pen):
    
    replaceable_insert = models.BooleanField(default=False)
    
    class Meta:
        specialization = 'ballpoint_pen'
 
#}

#{ Factories which are needed for testing:

def no_meta_factory():
    """Factory to mask TypeError in metaclass for testing"""
    
    class General(BaseGeneralizationModel):
        pass
    
    class Specialized(General):
        pass
    
    return Specialized


def no_specialization_factory():
    """Factory to mask TypeError in metaclass for testing"""
    
    class General(BaseGeneralizationModel):
        pass
    
    class Specialized(General):
        class Meta:
            verbose_name = 'my_model'
    
    return Specialized

def invalid_specialization_factory():
    """Factory to mask ValueError in metaclass for testing"""
    
    class General(BaseGeneralizationModel):
        pass
    
    class Specialized(General):
        class Meta:
            specialization = 'Naughty specialization!'
    
    return Specialized

def abstract_specialization_factory():
    """Factory to mask TypeError on incorrect specialization declaration"""
    
    class Abstract(BaseGeneralizationModel):
        class Meta:
            abstract = True
            specialization = 'abstract'
            
    return Abstract
    
def base_generalization_with_specialization_factory():
    """
    Factory to make a direct subclass of BaseGeneralizationModel which
    incorrectly declares specializations.
    
    """
    
    class General(BaseGeneralizationModel):
        
        class Meta:
            specialization = 'general'
    
    return General

#}