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

from django.db.models.manager import Manager

from djeneralize.query import SpecializedQuerySet

__all__ = ['SpecializationManager']

class SpecializationManager(Manager):
    """
    Customized manager to ensure that any QuerySet that is used always returns
    specialized model instances rather than generalized model instances.
    
    The manager can either return *final_specializations*, i.e. the most
    specialized specialization, or the direct specialization of the general
    model.
    
    """
    
    def __init__(self):
        """
        :param final_specialization: Whether the specializations returned are
            the most specialized specializations or whether the direct
            specializations are used
        :type final_specialization: :class:`bool`
        
        """
        
        super(SpecializationManager, self).__init__()
        
    
    def get_query_set(self):
        """
        Instead of returning a QuerySet, use SpecializedQuerySet instead
        
        :return: A specialized queryset
        :rtype: :class:`SpecializedQuerySet`
        
        """

        return SpecializedQuerySet(self.model)
    
    def direct(self):
        """
        Set the _final_specialization attribute on a clone of the queryset to
        ensure only directly descended specializations are considered.
        
        :return: The cloned queryset
        :rtype: :class:`SpecializedQuerySet`
        
        """
        
        return self.get_query_set().direct()
    
    def final(self):
        """
        Set the _final_specialization attribute on a clone of the queryset to
        ensure only terminal specializations are considered.
        
        :return: The cloned queryset
        :rtype: :class:`SpecializedQuerySet`
        
        """
        
        return self.get_query_set().final()
