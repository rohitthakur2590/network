#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# utils
from ansible.module_utils.network.common.utils import dict_diff
from ansible.module_utils.six import iteritems


def search_obj_in_list(name, lst, key='name'):
    for item in lst:
        if item[key] == name:
            return item
    return None


def search_dict_in_list(ca_type, ca_value, lst, key1='ca_type', key2='ca_value'):
    dct = next((item for item in lst if item[key1] == ca_type and item[key2] == ca_value), None)
    if dct:
        return dct
    else:
        return None


def coordinate_diff_have_only(have_key, have_value, want_dict):
    for key, value in iteritems(want_dict):
        if key == have_key and value == have_value:
            return False
    return True


def add_disable(name, want_item, have_item):
    commands = []
    if want_item['enable'] != have_item['enable']:
        if want_item['enable']:
            commands.append('delete service lldp interface ' + name + ' disable')
        else:
            commands.append('set service lldp interface ' + name + ' disable')
    return commands


def delete_disable(want_item):
    commands = []
    name = want_item['name']
    if not want_item['enable']:
        commands.append('delete service lldp interface ' + name + ' disable')
    return commands


def add_location(name, want_item, have_item):
    commands = []
    have_dict = {}
    have_ca = {}
    set_cmd = 'set service lldp interface ' + name
    want_location_type = want_item.get('location') or {}
    have_location_type = have_item.get('location') or {}

    if want_location_type['coordinate_based']:
        want_dict = want_location_type.get('coordinate_based') or {}
        if is_sub_dict_valid(have_location_type, 'coordinate_based'):
            have_dict = have_location_type.get('coordinate_based') or {}
        location_type = 'coordinate-based'
        updates = dict_diff(have_dict, want_dict)
        for key, value in iteritems(updates):
            if value:
                commands.append(set_cmd + ' location ' + location_type + ' ' + key + ' ' + str(value))

    elif want_location_type['civic_based']:
        location_type = 'civic-based'
        want_dict = want_location_type.get('civic_based') or {}
        want_ca = want_dict.get('ca_info') or []
        if is_sub_dict_valid(have_location_type, 'civic_based'):
            have_dict = have_location_type.get('civic_based') or {}
            have_ca = have_dict.get('ca_info') or []
            if want_dict['country_code'] != have_dict['country_code']:
                commands.append(set_cmd + ' location ' + location_type + ' country-code ' + str(want_dict['country_code']))
        else:
            commands.append(set_cmd + ' location ' + location_type + ' country-code ' + str(want_dict['country_code']))
        commands.extend(add_civic_address(name, want_ca, have_ca))

    elif want_location_type['elin']:
        location_type = 'elin'
        if is_sub_dict_valid(have_location_type, 'elin'):
            if want_location_type.get('elin') != have_location_type.get('elin') :
                new_i = '%010d' % (int('0000000000') + want_location_type['elin'])
                #commands.append(set_cmd + ' location ' + location_type + ' ' + str(want_location_type['elin']))
                commands.append(set_cmd + ' location ' + location_type + ' ' + str(new_i))
        else:
            commands.append(set_cmd + ' location ' + location_type + ' ' + str(want_location_type['elin']))
    return commands


def is_sub_dict_valid(dict, key):
    for item in dict:
        if item == key:
            return True
    return False


def update_location(name, want_item, have_item):
    commands = []
    del_cmd = 'delete service lldp interface ' + name
    want_location_type = want_item.get('location') or {}
    have_location_type = have_item.get('location') or {}

    if want_location_type['coordinate_based']:
        want_dict = want_location_type.get('coordinate_based') or {}
        if is_sub_dict_valid(have_location_type, 'coordinate_based'):
            have_dict = have_location_type.get('coordinate_based') or {}
            location_type = 'coordinate-based'
            for key, value in iteritems(have_dict):
                only_in_have = coordinate_diff_have_only(key, value, want_dict)
                if only_in_have:
                    commands.append(del_cmd + ' location ' + location_type + ' ' + key + ' ' + str(value))
        else:
            commands.append(del_cmd + ' location')

    elif want_location_type['civic_based']:
        want_dict = want_location_type.get('civic_based') or {}
        want_ca = want_dict.get('ca_info') or []
        if is_sub_dict_valid(have_location_type, 'civic_based'):
            have_dict = have_location_type.get('civic_based') or {}
            have_ca = have_dict.get('ca_info')
            commands.extend(update_civic_address(name, want_ca, have_ca))
        else:
            commands.append(del_cmd + ' location')

    else:
        if is_sub_dict_valid(have_location_type, 'elin'):
            if want_location_type.get('elin') != have_location_type.get('elin'):
                commands.append(del_cmd + ' location')
        else:
            commands.append(del_cmd + ' location')
    return commands


def delete_location(want_item):
    commands = []
    name = want_item['name']
    del_cmd = 'delete service lldp interface ' + name + ' location'
    want_location_type = want_item.get('location') or {}
    if want_location_type :
        commands.append(del_cmd)
    return commands


def add_civic_address(name, want, have):
    commands = []
    for item in want:
        ca_type = item['ca_type']
        ca_value = item['ca_value']
        obj_in_have = search_dict_in_list(ca_type,ca_value,have)
        if not obj_in_have:
            commands.append('set service lldp interface ' + name + ' location civic-based ca-type ' + str(ca_type) + ' ca-value ' + ca_value)
    return commands


def update_civic_address(name, want, have):
    commands = []
    for item in have:
        ca_type = item['ca_type']
        ca_value = item['ca_value']
        in_want = search_dict_in_list(ca_type,ca_value,want)
        if not in_want:
            commands.append('delete service lldp interface ' + name + ' location civic-based ca-type ' + str(ca_type))
    return commands

