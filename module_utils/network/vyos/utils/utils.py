#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# utils
from ansible.module_utils.six import iteritems


def search_obj_in_list(name, lst, key='name'):
    for item in lst:
        if item[key] == name:
            return item
    return None


def search_dict_tv_in_list(type, value, lst, key1, key2):
    obj = next((item for item in lst if item[key1] == type and item[key2] == value), None)
    if obj:
        return obj
    else:
        return None


def key_value_in_dict(have_key, have_value, want_dict):
    for key, value in iteritems(want_dict):
        if key == have_key and value == have_value:
            return True
    return False


def is_dict_element_present(dict, key):
    for item in dict:
        if item == key:
            return True
    return False





