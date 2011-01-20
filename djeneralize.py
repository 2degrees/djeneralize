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

from collections import defaultdict

from django.db.models.base import ModelBase, Model
from django.db.models.fields import FieldDoesNotExist, TextField
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.db.models import signals

__all__ = [
    'BaseGeneralizationMeta', 'BaseGeneralizationModel', 'SpecializedQuerySet',
    'SpecializationManager',
    ]

# { Metaclass:
    
class BaseGeneralizationMeta(ModelBase):
    
    def __new__(cls, name, bases, attrs):
        
        # Get the declared Meta inner class before the super-metaclass removes
        # it:
        meta = attrs.get('Meta')
        
        # We must remove the specialization declarations from the Meta inner
        # class since ModelBase will raise a TypeError is it encounters these:
        if meta:
            specialization = meta.__dict__.pop('specialization', None)
        else:
            specialization = None 
        
        new_model = super(BaseGeneralizationMeta, cls).__new__(
            cls, name, bases, attrs
            )
        
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
            
            # Add the as_specialization method for the General model:
            new_model.as_specialization = _get_as_specialization
            
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
            
            # Update the specializations mapping on the General model so that it
            # knows to use this class for that specialization:
            parent_class = new_model.__base__
            parent_class._meta.specializations[specialization] = new_model         
            
            # It might be useful to set this on the _meta of this class for
            # book-keeping, although I can't think of a use at present as this
            # should be stored on the actual model as _specialization:
            new_model._meta.specialization = specialization
        
        return new_model

#}

# { Customized queryset

class SpecializedQuerySet(QuerySet):
    """
    A wrapper around QuerySet to ensure Specialized Models are returned.
    
    """
    
    def __iter__(self):
        """
        Override the iteration to ensure what's returned are Specialized Model
        instances.
        
        """
        
        # Get the resource ids and types together:
        specializations_by_id = self._clone().values_list(
            'specialization_type', 'id'
            )
        
        # Transform this into a dictionary of IDs by type:
        ids_by_specialization = defaultdict(list)
        
        # and keep track of the IDs which respect the ordering specified in the
        # queryset:
        specialization_ids = []
        
        for specialization, id in specializations_by_id:
            ids_by_specialization[specialization].append(id)
            specialization_ids.append(id) 
        
        specialized_model_instances = {}
        
        # Add the sub-class instances into a single look-up 
        for specialization, ids in ids_by_specialization.items():
            sub_instances = self.model._meta.specialization[
                specialization
                ].objects.in_bulk(ids)
            
            specialized_model_instances.update(sub_instances)
        
        for resource_id in specialization_ids:
            yield specialized_model_instances[resource_id]
            
    def get(self, *args, **kwargs):
        """
        Override get to ensure a specialized model instance is returned.
        
        :return: A specialized model instance
        
        """
        
        if 'specialization_type' in kwargs:
            # if the specialization is explicitly specified, use this to work out
            # which sub-class of the general model we'll use:
            specialization = kwargs.pop('specialization_type')
        else:
            try:
                specialization = super(SpecializedQuerySet, self)\
                    .filter(*args, **kwargs).values_list(
                        'specialization_type', flat=True
                        )[0]
            except IndexError:
                raise self.model.DoesNotExist(
                    "%s matching query does not exist." %
                    self.model._meta.object_name
                    )
        
        try:
            return self.model._meta.specialization[specialization]\
                                   .objects.get(*args, **kwargs)
        except KeyError:
            raise self.model.DoesNotExist("%s matching query does not exist." %
                                          self.model._meta.object_name)
            
    # TODO: Override __getitem__
    # TODO: Ensure that all annotations and extra fields are copied

#}


# { Manager:

class SpecializationManager(Manager):
    """
    Customized manager to ensure that any QuerySet that is used always returns
    specialized model instances rather than generalized model instances.
    
    """
    
    def get_query_set(self):
        """
        Instead of returning a QuerySet, use SpecializedQuerySet instead
        
        :return: A specialized queryset
        :rtype: :class:`SpecializedQuerySet`
        
        """
        
        return SpecializedQuerySet(self.model)

#}

# { Base abstract model:

class BaseGeneralizationModel(Model):
    """Base model from which all Generalized and Specialized models inherit"""
    
    
    __metaclass__ = BaseGeneralizationMeta
    
    specialization_type = TextField(db_index=True)
    """Field to store the specialization"""
    
    class Meta:
        abstract = True

#}

# { Signal handler 

def ensure_specialization_manager(sender, **kwargs):
    """
    Ensure that a BaseGeneralizationModel subclass contains a default
    specialization manager and sets the ``_default_specialization_manager``
    attribute on the class.
    
    :param sender: The class which emitted the class prepared signal which needs
        to be checked for the specialization manager
    :type sender: :class:`django.db.models.base.Model`
    
    """
    
    cls = sender
    
    if not isinstance(cls, BaseGeneralizationModel):
        return
    
    if cls._meta.abstract:
        return
    if not getattr(cls, '_default_specialization_manager', None):
        # Create the default specialization manager, if needed.
        try:
            cls._meta.get_field('specializations')
            raise ValueError(
                "Model %s must specify a custom SpecializationManager, because "
                "it has a field named 'objects'" % cls.__name__
                )
        except FieldDoesNotExist:
            pass
        cls.add_to_class('specializations', SpecializationManager())
        cls._base_specializations_manager = cls.specializations
    elif not getattr(cls, '_base_specializations_manager', None):
        default_specialization_mgr = cls._default_specializations_manager.__class__
        if (default_specialization_mgr is SpecializationManager or
                getattr(default_specialization_mgr, "use_for_related_fields", False)):
            cls._base_specializations_manager = cls._default_specialization_manager
        else:
            # Default manager isn't a plain Manager class, or a suitable
            # replacement, so we walk up the base class hierarchy until we hit
            # something appropriate.
            for base_class in default_specialization_mgr.mro()[1:]:
                if (base_class is SpecializationManager or
                        getattr(base_class, "use_for_related_fields", False)):
                    cls.add_to_class('_base_specializations_manager', base_class())
                    return
            raise AssertionError(
                "Should never get here. Please report a bug, including your "
                "model and model manager setup."
                )

signals.class_prepared.connect(ensure_specialization_manager)

#}

# { Utility functions 

def _get_as_specialization(self):
    """
    Get the specialized model instance which corresponds to the general case.
    
    :return: The specialized model corresponding to the current model
    
    """
    
    return self._meta.specializations[self.specialization_type].objects.get(
        pk=self.pk
        )

#}