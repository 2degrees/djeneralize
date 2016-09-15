# -*- coding: utf-8 -*-
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

from collections import defaultdict

from django.db.models.query import QuerySet

from djeneralize import PATH_SEPARATOR
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

        # Determine whether there are any extra fields which are also required
        # to order the queryset. This is needed as Django's implementation of
        # ValuesQuerySet cannot cope with fields being omitted which are used in
        # the ordering and originating from an extra select
        extra_fields = set(self.query.extra.keys())
        ordering_fields = set(
            field.lstrip('-') for field in self.query.order_by)
        extra_ordering_fields = list(extra_fields & ordering_fields)

        values_query_fields = ['specialization_type', 'id'] + \
            extra_ordering_fields

        # Get the resource ids and types together
        specializations_data = self._clone().values(*values_query_fields)

        # Transform this into a dictionary of IDs by type:
        ids_by_specialization = defaultdict(list)

        # and keep track of the IDs which respect the ordering specified in the
        # queryset:
        specialization_ids = []

        for specialization_data in specializations_data:
            specialization_type = specialization_data['specialization_type']
            specialization_id = specialization_data['id']

            ids_by_specialization[specialization_type].append(specialization_id)
            specialization_ids.append(specialization_id)

        specialized_model_instances = {}

        # Add the sub-class instances into a single look-up
        for specialization, ids in ids_by_specialization.items():
            if not self._final_specialization:
                # Coerce the specialization to only be the direct child of the
                # general model (self.model):
                specialization = find_next_path_down(
                    self.model.model_specialization, specialization,
                    PATH_SEPARATOR
                    )

            sub_queryset = self.model._meta.specializations[
                specialization
                ].objects.all()

            # Copy any deferred loading over to the new querysets:
            sub_queryset.query.deferred_loading = self.query.deferred_loading

            # Copy any extra select statements to the new querysets. NB: It
            # doesn't make sense to copy any of the "where", "tables" or
            # "order_by" options as these have already been applied in the
            # parent queryset
            sub_queryset.query._extra = self.query._extra

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
                self.model.model_specialization, specialization, PATH_SEPARATOR
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
