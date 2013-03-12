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
from django.db import models
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor


__all__ = ["SpecializedForeignKey"]


#{ Fields


class SpecializedForeignKey(models.ForeignKey):
    """
    Foreign key field that return the most specialized model instance of the
    related object.
    
    """
    
    def contribute_to_class(self, cls, name):
        super(SpecializedForeignKey, self).contribute_to_class(cls, name)
        descriptor = SpecializedReverseSingleRelatedObjectDescriptor(self)
        setattr(cls, self.name, descriptor)


#{ Field descriptor


class SpecializedReverseSingleRelatedObjectDescriptor(
    ReverseSingleRelatedObjectDescriptor):
    """
    Make the specialized related-object manager available as attribute on a
    model class.
    
    """
    
    def __get__(self, instance, instance_type=None):
        super_descriptor = \
            super(SpecializedReverseSingleRelatedObjectDescriptor, self)
            
        related_object = super_descriptor.__get__(instance, instance_type)
        try:
            return related_object.get_as_specialization()
        except KeyError:
            # In case the object is already the most specialized instance
            # KeyError is raised
            return related_object

#}
