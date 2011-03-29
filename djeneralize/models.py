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
import re

from django.db.models.base import ModelBase, Model
from django.db.models.fields import FieldDoesNotExist, TextField
from django.dispatch import Signal

from djeneralize import PATH_SEPERATOR
from djeneralize.manager import SpecializationManager
from djeneralize.utils import find_next_path_down

__all__ = ['BaseGeneralizationMeta', 'BaseGeneralizationModel']

SPECIALIZATION_RE = re.compile(r'^\w+$')
"""Allowed characters in the specializations declaration in class Meta"""

# { Custom signal

specialized_model_prepared = Signal()
"""Signal to be emitted when a specialized model has been prepared"""

#}

# { Metaclass:
    
class BaseGeneralizationMeta(ModelBase):
    """The metaclass for BaseGeneralizedModel"""
    
    def __new__(cls, name, bases, attrs):
        super_new = super(BaseGeneralizationMeta, cls).__new__
        parents = [b for b in bases if isinstance(b, BaseGeneralizationMeta)]
        
        # Get the declared Meta inner class before the super-metaclass removes
        # it:
        meta = attrs.get('Meta')
        
        # We must remove the specialization declarations from the Meta inner
        # class since ModelBase will raise a TypeError is it encounters these:
        if meta:
            specialization = meta.__dict__.pop('specialization', None)
        else:
            specialization = None 
            
        #if name == "Fruit": import pdb; pdb.set_trace()
        new_model = super_new(cls, name, bases, attrs)
        
        # Ensure that the _meta attribute has some additional attributes:
        if not hasattr(new_model._meta, 'abstract_specialization_managers'):
            new_model._meta.abstract_specialization_managers = []
        if not hasattr(new_model._meta, 'concrete_specialization_managers'):
            new_model._meta.concrete_specialization_managers = []
        
        if not parents:
            return new_model
        
        if new_model._meta.abstract:
            # This is an abstract base-class and no specializations should be
            # declared on the inner class:
            if specialization is not None:
                # We need to ensure this is actually None and not just evaluates
                # to False as we enforce that it's not declared:
                raise TypeError(
                    "Abstract models should not have a specialization declared "
                    "on their inner Meta class"
                    )
        elif BaseGeneralizationModel in bases:
            # This must be a direct descendant from the BaseGeneralizationModel.
            # Prepare the look-up mapping of specializations which the sub-
            # classes will update:
            new_model._meta.specializations = {}
            new_model._meta.specialization = PATH_SEPERATOR
            
            if specialization is not None:
                # We need to ensure this is actually None and not just evaluates
                # to False as we enforce that it's not declared:
                raise TypeError(
                    "General models should not have a specialization declared "
                    "on their inner Meta class"
                    )
                
        else:
            if specialization is None:
                raise TypeError(
                    "Specialized models must declare specialization on their "
                    "inner Meta class"
                    )
            
            if not SPECIALIZATION_RE.match(specialization):
                raise ValueError("Specializations must be alphanumeric string")
            
            parent_class = new_model.__base__

            new_model._meta.specializations = {}
            new_model._generalized_parent = parent_class
            
            path_specialization = '%s%s%s' % (
                parent_class._meta.specialization, specialization,
                PATH_SEPERATOR
                )

            # Calculate the specialization as a path taking into account the
            # specialization of any ancestors:
            new_model._meta.specialization = path_specialization
            
            # Update the specializations mapping on the General model so that it
            # knows to use this class for that specialization:
            ancestor = getattr(new_model, '_generalized_parent', None)
            while ancestor:
                ancestor._meta.specializations[
                    new_model._meta.specialization
                    ] = new_model
                ancestor = getattr(ancestor, '_generalized_parent', None)
            
            parent_class._meta.specializations[path_specialization] = new_model
            
        is_proxy = new_model._meta.proxy
        
        if getattr(new_model, '_default_specialization_manager', None):
            if not is_proxy:
                new_model._default_specialization_manager = None
                new_model._base_specialization_manager = None
            else:
                new_model._default_specialization_manager = \
                    new_model._default_specialization_manager._copy_to_model(
                        new_model
                        )
                new_model._base_specialization_manager = \
                    new_model._base_specialization_manager._copy_to_model(
                        new_model
                        )
                    
        for obj_name, obj in attrs.items():
            # We need to do this to ensure that a declared SpecializationManager
            # will be correctly set-up:
            if isinstance(obj, SpecializationManager):
                new_model.add_to_class(obj_name, obj)
        
        for base in parents:
            # Inherit managers from the abstract base classes.
            new_model.copy_managers(
                base._meta.abstract_specialization_managers
                )

            # Proxy models inherit the non-abstract managers from their base,
            # unless they have redefined any of them.
            if is_proxy:
                new_model.copy_managers(
                    base._meta.concrete_specialization_managers
                    )
        
        specialized_model_prepared.send(sender=new_model)
        
        new_model.model_specialization = new_model._meta.specialization
        
        return new_model

#}

# { Base abstract model:

class BaseGeneralizationModel(Model):
    """Base model from which all Generalized and Specialized models inherit"""
    
    
    __metaclass__ = BaseGeneralizationMeta
    
    specialization_type = TextField(db_index=True)
    """Field to store the specialization"""
    
    def __init__(self, *args, **kwargs):
        """
        If specialization_type is not set in kwargs, add this is the most
        specialized model, set specialization_type to match the specialization
        declared in Meta
        
        """
                    
        super(BaseGeneralizationModel, self).__init__(*args, **kwargs)
        
        # If we have a final specialization, and a specialization_type is not
        # specified in kwargs, set it to the default for this model:
        if ('specialization_type' not in kwargs and
            not self._meta.specializations):
            self.specialization_type = self.__class__.model_specialization
        
    class Meta:
        abstract = True
        
    def get_as_specialization(self, final_specialization=True):
        """
        Get the specialized model instance which corresponds to the general
        case.
        
        :param final_specialization: Whether the specialization returned is
            the most specialized specialization or whether the direct
            specialization is used
        :type final_specialization: :class:`bool`
        :return: The specialized model corresponding to the current model
        
        """
        
        path = self.specialization_type
        
        if not final_specialization:
            # We need to find the path which is only one-step down from the
            # current level of specialization.
            path = find_next_path_down(
                self._meta.specialization, path, PATH_SEPERATOR
                )
    
        return self._meta.specializations[path].objects.get(pk=self.pk)
    
#}

# { Signal handler 

def ensure_specialization_manager(sender, **kwargs):
    """
    Ensure that a BaseGeneralizationModel subclass contains a default
    specialization manager and sets the ``_default_specialization_manager``
    attribute on the class.
    
    :param sender: The new specialized model
    :type sender: :class:`BaseGeneralizationModel`
    
    """
    
    cls = sender
    
    if cls._meta.abstract:
        return
    
    if not getattr(cls, '_default_specialization_manager', None):
        # Create the default specialization manager, if needed.
        try:
            cls._meta.get_field('specializations')
            raise ValueError(
                "Model %s must specify a custom SpecializationManager, because "
                "it has a field named 'specializations'" % cls.__name__
                )
        except FieldDoesNotExist:
            pass
        cls.add_to_class('specializations', SpecializationManager())
        cls._base_specialization_manager = cls.specializations
    elif not getattr(cls, '_base_specialization_manager', None):
        default_specialization_mgr = \
            cls._default_specialization_manager.__class__
        if default_specialization_mgr is SpecializationManager or getattr(
            default_specialization_mgr, "use_for_related_fields", False
            ):
            cls._base_specialization_manager = \
                cls._default_specialization_manager
        else:
            # Default manager isn't a plain Manager class, or a suitable
            # replacement, so we walk up the base class hierarchy until we hit
            # something appropriate.
            for base_class in default_specialization_mgr.mro()[1:]:
                if base_class is SpecializationManager or getattr(
                    base_class, "use_for_related_fields", False
                    ):
                    cls.add_to_class(
                        '_base_specialization_manager', base_class()
                        )
                    return
            raise AssertionError(
                "Should never get here. Please report a bug, including your "
                "model and model manager setup."
                )

specialized_model_prepared.connect(ensure_specialization_manager)
#}