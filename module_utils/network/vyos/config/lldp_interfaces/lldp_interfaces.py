#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The vyos_lldp_interfaces class
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created
"""
from ansible.module_utils.network.common.cfg.base import ConfigBase
from ansible.module_utils.network.vyos.facts.facts import Facts
from ansible.module_utils.network.common.utils import to_list
from ansible.module_utils.network. \
    vyos.utils.utils import search_obj_in_list, delete_location, \
    add_location, update_location, add_disable


class Lldp_interfaces(ConfigBase):
    """
    The vyos_lldp_interfaces class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'lldp_interfaces',
    ]

    params = ['location', 'name']
    set_cmd = 'set service lldp interface '
    del_cmd = 'delete lldp service interface '

    def __init__(self, module):
        super(Lldp_interfaces, self).__init__(module)

    def get_lldp_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: Th      e current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, \
                                                         self.gather_network_resources)
        lldp_interfaces_facts = facts['ansible_network_resources'].get('lldp_interfaces')
        if not lldp_interfaces_facts:
            return []
        return lldp_interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        result = {'changed': False}
        commands = list()
        warnings = list()
        existing_lldp_interfaces_facts = self.get_lldp_interfaces_facts()
        commands.extend(self.set_config(existing_lldp_interfaces_facts))
        if commands:
            if self._module.check_mode:
                resp = self._connection.edit_config(commands, commit=False)
            else:
                resp = self._connection.edit_config(commands)
            result['changed'] = True

        result['commands'] = commands

        if self._module._diff:
            result['diff'] = resp['diff'] if result['changed'] else None

        changed_lldp_interfaces_facts = self.get_lldp_interfaces_facts()
        result['before'] = existing_lldp_interfaces_facts
        if result['changed']:
            result['after'] = changed_lldp_interfaces_facts

        result['warnings'] = warnings
        return result

    def set_config(self, existing_lldp_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        want = self._module.params['config']
        have = existing_lldp_interfaces_facts
        resp = self.set_state(want, have)
        return to_list(resp)

    def set_state(self, want, have):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        state = self._module.params['state']
        if state == 'overridden':
            commands.extend(self._state_overridden(want=want, have=have))
        elif state == 'deleted':
            if want:
                for item in want:
                    name = item['name']
                    obj_in_have = search_obj_in_list(name, have)
                    commands.extend(self._state_deleted(have_lldp=obj_in_have))
            else:
                for item in have:
                    commands.extend(self._state_deleted(have_lldp=item))
        elif state == 'merged':
            for item in want:
                name = item['name']
                obj_in_have = search_obj_in_list(name, have)
                commands.extend(self._state_merged(want_lldp=item, have_lldp=obj_in_have))
        elif state == 'replaced':
            for item in want:
                name = item['name']
                obj_in_have = search_obj_in_list(name, have)
                commands.extend(self._state_replaced(want_lldp=item, have_lldp=obj_in_have))
        return commands

    @staticmethod
    def _state_replaced(**kwargs):
        """ The command generator when state is replaced

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        want_lldp = kwargs['want_lldp']
        have_lldp = kwargs['have_lldp']
        if have_lldp:
            commands.extend(
                Lldp_interfaces._render_del_commands(
                    want_element={'lldp': want_lldp},
                    have_element={'lldp': have_lldp}
                )
            )
        commands.extend(
            Lldp_interfaces._state_merged(
                want_lldp=want_lldp,
                have_lldp=have_lldp
            )
        )
        return commands

    @staticmethod
    def _state_overridden(**kwargs):
        """ The command generator when state is overridden

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []
        want_lldps = kwargs['want']
        have_lldps = kwargs['have']
        for have_lldp in have_lldps:
            lldp_name = have_lldp['name']
            lldp_in_want = search_obj_in_list(lldp_name, want_lldps)
            if not lldp_in_want:
                commands.extend(
                    Lldp_interfaces._purge_attribs(
                        lldp=have_lldp
                    )
                )

        for lldp in want_lldps:
            name = lldp['name']
            lldp_in_have = search_obj_in_list(name, have_lldps)
            commands.extend(
                Lldp_interfaces._state_replaced(
                    want_lldp=lldp,
                    have_lldp=lldp_in_have
                )
            )
        return commands

    @staticmethod
    def _state_merged(**kwargs):
        """ The command generator when state is merged

        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """

        commands = []
        want_lldp = kwargs['want_lldp']
        have_lldp = kwargs['have_lldp']
        if have_lldp:

            commands.extend(
                Lldp_interfaces._render_updates(
                    want_element={'lldp': want_lldp},
                    have_element={'lldp': have_lldp}
                )
            )
        else:
            commands.extend(
                Lldp_interfaces._render_set_commands(
                    want_element={
                        'lldp': want_lldp
                    }
                )
            )
        return commands

    @staticmethod
    def _state_deleted(**kwargs):
        """ The command generator when state is deleted

        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []

        have_lldp = kwargs['have_lldp']
        if have_lldp:
            commands.extend(Lldp_interfaces._purge_attribs(lldp=have_lldp))
        return commands

    @staticmethod
    def _render_updates(**kwargs):
        commands = []
        want_element = kwargs['want_element']
        have_element = kwargs['have_element']

        lldp_name = have_element['lldp']['name']

        have_item = have_element['lldp']
        want_item = want_element['lldp']

        '''
        want_enable = want_item.get('enable')
        have_enable = have_item.get('enable') or

        if want_enable['enable'] != have_enable['enable']:
            if want_enable:
                commands.append(Lldp_interfaces.del_cmd + lldp_name + ' disable ')
            else:
                commands.append(Lldp_interfaces.set_cmd + lldp_name + ' disable ')
        '''
        # handles the disable part
        commands.extend(add_disable(lldp_name, want_item, have_item))
        # handles the location config
        commands.extend(add_location(lldp_name, want_item, have_item))

        return commands

    @staticmethod
    def _render_set_commands(**kwargs):
        commands = []
        have_item = {}
        want_element = kwargs['want_element']
        lldp_name = want_element['lldp']['name']

        params = Lldp_interfaces.params
        want_item = want_element['lldp']

        commands.extend(add_location(lldp_name, want_item, have_item))
        for attrib in params:
            value = want_item[attrib]
            if value:
                if attrib == 'location':
                    commands.extend(add_location(lldp_name, want_item, have_item))
                elif attrib == 'enable':
                    if not value:
                        commands.append(Lldp_interfaces.set_cmd + lldp_name + ' disable ')
                else:
                    commands.append(Lldp_interfaces.set_cmd + lldp_name)

        return commands

    @staticmethod
    def _purge_attribs(**kwargs):
        commands = []
        lldp = kwargs['lldp']

        for item in Lldp_interfaces.params:
            if lldp.get(item):
                if item == 'location':
                    commands.extend(delete_location(lldp))
        return commands

    @staticmethod
    def _render_del_commands(**kwargs):
        commands = []
        want_element = kwargs['want_element']
        have_element = kwargs['have_element']

        lldp_name = have_element['lldp']['name']
        params = Lldp_interfaces.params

        have_item = have_element['lldp']
        want_item = want_element['lldp']

        for attrib in params:
            if attrib == 'location':
                commands.extend(update_location(lldp_name, want_item, have_item))
        return commands
