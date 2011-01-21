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

"""Utilities for djeneralize"""

__all__ = ['find_next_path_down']


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