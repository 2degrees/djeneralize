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
from django.db.models.fields.related import (
    ReverseSingleRelatedObjectDescriptor, ForeignRelatedObjectsDescriptor)


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

    def contribute_to_related_class(self, cls, related):
        """
        Ensure that specializations are return for related object lookups.
        
        Copied from Django's :class:`django.db.models.ForeignKey`.
        
        """
        if not self.rel.is_hidden():
            # Hidden FKs don't get a related descriptor
            descriptor = SpecializedForeignRelatedObjectsDescriptor(related)
            setattr(cls, related.get_accessor_name(), descriptor)
        
        if self.rel.field_name is None:
            self.rel.field_name = cls._meta.pk.name

#{ Field descriptors


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


class SpecializedForeignRelatedObjectsDescriptor(
    ForeignRelatedObjectsDescriptor):
    """
    Make the specialized related-object manager available as attribute on a
    model class.
    
    """
    
    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        return self.create_manager(
            instance,
            self.related.model._default_specialization_manager.__class__,
            )


#}
