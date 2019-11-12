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
import os
import uuid

import ansible_runner

from network_runner import exceptions

from network_runner.models.playbook import Playbook
from network_runner.models.inventory import Inventory
from network_runner.models.inventory import Host


IMPORT_ROLE = 'import_role'
NETWORK_RUNNER = 'network-runner'


def run(playbook, inventory, quiet=True):
    """Execute a playbook with inventory

    :param playbook: the playbook to run
    :type playbook: `network_runner.resources.playbook:Playbook`

    :param inventory: the inventory to run the playbook against
    :type inventory: `network_runner.resources.inventory:Inventory`

    :param quiet: control whether or not playbook output is displayed
    :type quiet: bool

    :returns: the result from runner
    :rtype: `ansible_runner.interface:Runner`
    """
    assert isinstance(playbook, Playbook)
    assert isinstance(inventory, Inventory)

    data_dir = os.path.join(
        os.path.expanduser('~/.network-runner'), str(uuid.uuid4())
    )

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # invoke ansible networking via ansible runner
    result = ansible_runner.run(playbook=playbook.serialize(),
                                inventory=inventory.serialize(),
                                quiet=quiet,
                                private_data_dir=data_dir,
                                settings={'pexpect_use_poll': False})

    # check for failure
    if result.status == 'failed' or \
            (result.stats and result.stats.get('failures', [])):
        raise exceptions.NetworkRunnerException(' '.join(result.stdout))

    return result


class NetworkRunner(object):
    """Object to invoke ansible_runner to call Ansible Networking
    Hold inventory and provide an interface for calling
    roles in Ansible Networking to manipulate switch configuration
    """

    def __init__(self, inventory=None):
        if inventory is not None:
            assert isinstance(inventory, Inventory)
        self.inventory = inventory or Inventory()

    def add_host(self, host):
        """Add host to inventory

        Adds a new ```Host``` instance to the current inventory
        object.  The value must be a value ```Host``` instance.

        :param host: A valid instance of ```Host```
        :type host: network_runner.models.inventory.hosts.Host

        :returns: None
        """
        assert isinstance(host, Host)
        self.inventory.hosts[host.name] = host

    def play(self, action, hosts=None, variables=None):
        """Play a set of tasks from the role

        :param tasks_from: the task to play
        :type tasks_from: str

        :param hosts: the hosts to execute against
        :type hosts: str

        :param variables: values to be passed into the play
        :type variables: dict

        :returns: the results of the playbook run
        :rtype: AnsibleRunner
        """
        pb = Playbook()
        play = pb.new(hosts=(hosts or 'all'), gather_facts=False)

        role = play.roles.new(role=NETWORK_RUNNER)
        role.vars = variables

        if variables is None:
            variables = {}

        variables['network_action'] = action
        role.vars = variables

        return run(pb, self.inventory)

    def create_vlan(self, hostname, vlan_id, vlan_name=None):
        """Create VLAN.

        :param hostname: The name of the host in Ansible inventory.
        :param vlan_id: The VLAN's ID to create.
        :param vlan_name: The VLAN's name/description.
        """
        variables = {'vlan_id': vlan_id, 'vlan_name': vlan_name}
        return self.play('create_vlan', hostname, variables)

    def delete_vlan(self, hostname, vlan_id):
        """Delete VLAN.

        :param hostname: The name of the host in Ansible inventory.
        :param vlan_id: The VLAN's ID to delete.
        """
        return self.play('delete_vlan', hostname, {'vlan_id': vlan_id})

    def conf_access_port(self, hostname, port, vlan_id):
        """Configure access port on a vlan.

        :param hostname: The name of the host in Ansible inventory.
        :param port: The port to configure.
        :param vlan_id: The vlan_id to assign to the port.
                        An empty or None value will default to the
                        target device's default VLAN assignment. This
                        default is assigned in the ansible role.
        """
        variables = {'vlan_id': vlan_id, 'port_name': port,
                     'port_description': port}
        return self.play('conf_access_port', hostname, variables)

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
        variables = {'vlan_id': vlan_id, 'port_name': port,
                     'port_description': port, 'trunked_vlans': trunked_vlans}
        return self.play('conf_trunk_port', hostname, variables)

    def delete_port(self, hostname, port):
        """Delete port configuration.

        :param hostname: The name of the host in Ansible inventory.
        :param port: The port to configure.
        """
        return self.play('delete_port', hostname, {'port_name': port})
