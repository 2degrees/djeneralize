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

"""Utilities for djeneralize"""

from django.http import Http404

__all__ = ['find_next_path_down', 'get_specialization_or_404']


def find_next_path_down(current_path, path_to_reduce, separator):
    """
    Manipulate ``path_to_reduce`` so that it only contains one more level of
    detail than ``current_path``.

    :param current_path: The path used to determine the current level
    :type current_path: :class:`basestring`
    :param path_to_reduce: The path to find the next level down
    :type path_to_reduce: :class:`basestring`
    :param separator: The string used to separate the parts of path
    :type separator: :class:`basestring`
    :return: The path one level deeper than that of ``current_path``
    :rtype: :class:`unicode`

    """

    # Determine the current and next levels:
    current_level = current_path.count(separator)
    next_level = current_level + 1

    # Reduce the path to reduce down to just one more level deep than the
    # current path depth:
    return u'%s%s' % (
        separator.join(
            path_to_reduce.split(separator, next_level)[:next_level]
            ), separator
        )


def _get_queryset(klass):
    """
    Returns a SpecializedQuerySet from a BaseGeneralizedModel sub-class,
    SpecializationManager, or SpecializedQuerySet.

    """

    # Need to import here to stop circular import problems
    # TODO: move this functionality to a separate module
    from djeneralize.manager import SpecializationManager
    from djeneralize.query import SpecializedQuerySet


    if isinstance(klass, SpecializedQuerySet):
        return klass
    elif isinstance(klass, SpecializationManager):
        manager = klass
    else:
        manager = klass._default_specialization_manager
    return manager.all()


def get_specialization_or_404(klass, *args, **kwargs):
    """
    Uses get() to return an specializaed object, or raises a Http404 exception
    if the object does not exist.

    klass may be a BaseGeneralizedModel, SpecializationManager, or
    SpecializedQuerySet object. All other passed arguments and keyword arguments
    are used in the get() query.

    .. note:: Like with get(), an MultipleObjectsReturned will be raised if more
        than one object is found.

    """
    queryset = _get_queryset(klass)

    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise Http404(
            'No %s matches the given query.' % queryset.model._meta.object_name
            )
