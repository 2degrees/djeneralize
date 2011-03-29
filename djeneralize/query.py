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

from django.db.models.query import QuerySet

from djeneralize import PATH_SEPERATOR
from djeneralize.utils import find_next_path_down

__all__ = ['SpecializedQuerySet']


class SpecializedQuerySet(QuerySet):
    """
    A wrapper around QuerySet to ensure specialized models are returned.
    
    """
    
    def __init__(self, *args, **kwargs):
        """
        :param final_specialization: Whether the specializations returned are
            the most specialized specializations or whether the direct
            specializations are used
        :type final_specialization: :class:`bool`
        
        """
        
        final_specialization = kwargs.pop('final_specialization', True)
        
        super(SpecializedQuerySet, self).__init__(*args, **kwargs)
        self._final_specialization = final_specialization
    
    def iterator(self):
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
            if not self._final_specialization:
                # Coerce the specialization to only be the direct child of the
                # general model (self.model):
                specialization = find_next_path_down(
                    self.model.model_specialization, specialization,
                    PATH_SEPERATOR
                    )
            
            sub_queryset = self.model._meta.specializations[
                specialization
                ].objects.all()
                
            # Copy any deferred loading over to the new querysets:
            sub_queryset.query.deferred_loading = self.query.deferred_loading 
            
            sub_instances = sub_queryset.in_bulk(ids)
            
            specialized_model_instances.update(sub_instances)
        
        for resource_id in specialization_ids:
            yield specialized_model_instances[resource_id]
            
    def annotate(self, *args, **kawrgs):
        raise NotImplementedError(
            "%s does not support annotations as these cannot be reliably copied"
            " to the specialized instances" % self.__class__.__name__                    
            )
    
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
        
        if not self._final_specialization:
            # Coerce the specialization to only be the direct child of the
            # general model (self.model):
            specialization = find_next_path_down(
                self.model.model_specialization, specialization, PATH_SEPERATOR
                )
        
        try:
            return self.model._meta.specializations[specialization]\
                                   .objects.get(*args, **kwargs)
        except KeyError:
            raise self.model.DoesNotExist("%s matching query does not exist." %
                                          self.model._meta.object_name)
    def direct(self):
        """
        Set the _final_specialization attribute on a clone of this queryset to
        ensure only directly descended specializations are considered.
        
        :return: The cloned queryset
        :rtype: :class:`SpecializedQuerySet`
        
        """
        
        clone = self._clone()
        clone._final_specialization = False
        return clone
    
    def final(self):
        """
        Set the _final_specialization attribute on a clone of this queryset to
        ensure only terminal specializations are considered.
        
        :return: The cloned queryset
        :rtype: :class:`SpecializedQuerySet`
        
        """
        
        clone = self._clone()
        clone._final_specialization = True
        return clone
            
    def _clone(self, klass=None, setup=False, **kwargs):
        """
        Customize the _clone method of QuerySet to ensure the value of
        _final_specialization is copied across to the clone correctly.
        
        :rtype: :class:`SpecializedQuerySet`
        
        """
        
        clone = super(SpecializedQuerySet, self)._clone(klass, setup, **kwargs)
        clone._final_specialization = self._final_specialization
        
        return clone