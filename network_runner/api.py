#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import ansible_runner

from network_runner import exceptions
from network_runner.resources.ansible import Playbook
from network_runner.resources.ansible.playbook import Play
from network_runner.resources.ansible.playbook import Task
from network_runner.resources.inventory import Inventory

IMPORT_ROLE = 'import_role'
NETWORK_RUNNER = 'network-runner'
NETWORK_CLI = 'network_cli'


class NetworkRunner(object):
    """Object to invoke ansible_runner to call Ansible Networking
    Hold inventory and provide an interface for calling
    roles in Ansible Networking to manipulate switch configuration
    """

    def __init__(self, inventory):
        assert isinstance(inventory, Inventory)
        self.inventory = inventory

    def run(self, playbook):
        assert isinstance(playbook, Playbook)

        # invoke ansible networking via ansible runner
        result = ansible_runner.run(playbook=playbook.serialize(),
                                    inventory=self.inventory.serialize(),
                                    settings={'pexpect_use_poll': False})

        # check for failure
        if result.status == 'failed' or \
                (result.stats and result.stats.get('failures', [])):
            raise exceptions.AnsibleRunnerException(' '.join(result.stdout))

        return result

    def create_vlan(self, hostname, vlan_id, vlan_name=None):
        """Create VLAN.

        :param hostname: The name of the host in Ansible inventory.
        :param vlan_id: The VLAN's ID to create.
        :param vlan_name: The VLAN's name/description.
        """
        play = Play(name='Create VLAN using {}'.format(NETWORK_CLI),
                    hosts=hostname,
                    connection=NETWORK_CLI,
                    gather_facts=False)

        task = Task(name='Create VLAN',
                    module=IMPORT_ROLE,
                    args={'name': NETWORK_RUNNER,
                          'tasks_from': 'create_vlan'},
                    vars={'vlan_id': vlan_id})

        play.tasks.add(task)

        playbook = Playbook()
        playbook.add(play)

        return self.run(playbook)

    def delete_vlan(self, hostname, vlan_id):
        """Delete VLAN.

        :param hostname: The name of the host in Ansible inventory.
        :param vlan_id: The VLAN's ID to delete.
        """
        play = Play(name='Delete VLAN using {}'.format(NETWORK_CLI),
                    hosts=hostname,
                    connection=NETWORK_CLI,
                    gather_facts=False)

        task = Task(name='Delete VLAN',
                    module=IMPORT_ROLE,
                    args={'name': NETWORK_RUNNER,
                          'tasks_from': 'delete_vlan'},
                    vars={'vlan_id': vlan_id})

        play.tasks.add(task)

        playbook = Playbook()
        playbook.add(play)

        return self.run(playbook)

    def conf_access_port(self, hostname, port, vlan_id):
        """Configure access port on a vlan.

        :param hostname: The name of the host in Ansible inventory.
        :param port: The port to configure.
        :param vlan_id: The vlan_id to assign to the port.
                        An empty or None value will default to the
                        target device's default VLAN assignment. This
                        default is assigned in the ansible role.
        """
        play_name = 'Configure port in access mode using {}'.format(
            NETWORK_CLI)
        play = Play(name=play_name,
                    hosts=hostname,
                    connection=NETWORK_CLI,
                    gather_facts=False)

        task = Task(name='Configure port in access mode',
                    module=IMPORT_ROLE,
                    args={'name': NETWORK_RUNNER,
                          'tasks_from': 'conf_access_port'},
                    vars={'vlan_id': vlan_id,
                          'port': port})

        play.tasks.add(task)

        playbook = Playbook()
        playbook.add(play)

        return self.run(playbook)

    def conf_trunk_port(self, hostname, port, vlan_id, trunked_vlans):
        """Configure trunk port w/ default vlan and optional additional vlans

        :param hostname: The name of the host in Ansible inventory.
        :param port: The port to configure.
        :param vlan_id: the default VLAN ID to assign to the port
                        An empty or None value will default to the
                        target device's default VLAN assignment. This
                        default is assigned in the ansible role.
        :param trunked_vlans: A list of VLAN IDs to add to the port in
                              addition to the default VLAN.
        """
        play_name = 'Configure port in trunk mode using {}'.format(
            NETWORK_CLI)
        play = Play(name=play_name,
                    hosts=hostname,
                    connection=NETWORK_CLI,
                    gather_facts=False)

        task = Task(name='Configure port in trunk mode',
                    module=IMPORT_ROLE,
                    args={'name': NETWORK_RUNNER,
                          'tasks_from': 'conf_trunk_port'},
                    vars={'vlan_id': vlan_id,
                          'port': port,
                          'trunked_vlans': trunked_vlans})

        play.tasks.add(task)

        playbook = Playbook()
        playbook.add(play)

        return self.run(playbook)

    def delete_port(self, hostname, port):
        """Delete port configuration.

        :param hostname: The name of the host in Ansible inventory.
        :param port: The port to configure.
        """
        play = Play(name='Delete port using {}'.format(NETWORK_CLI),
                    hosts=hostname,
                    connection=NETWORK_CLI,
                    gather_facts=False)

        task = Task(name='Delete port',
                    module=IMPORT_ROLE,
                    args={'name': NETWORK_RUNNER,
                          'tasks_from': 'delete_port'},
                    vars={'port': port})

        play.tasks.add(task)

        playbook = Playbook()
        playbook.add(play)

        return self.run(playbook)
