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
import sys

from network_runner import exceptions
from network_runner.formats import format_port_config

from network_runner.models.playbook import Playbook

from network_runner.models.inventory import Inventory
from network_runner.models.inventory import Host

ALL = 'all'
IMPORT_ROLE = 'import_role'
NETWORK_RUNNER = 'network-runner'
CREATE_VLAN = 'create_vlan'
DELETE_VLAN = 'delete_vlan'
LIST_VLANS = 'list_vlans'
CONF_ACCESS_PORT = 'conf_access_port'
CONF_TRUNK_PORT = 'conf_trunk_port'
ADD_TRUNK_VLAN = 'add_trunk_vlan'
DELETE_TRUNK_VLAN = 'delete_trunk_vlan'
DELETE_PORT = 'delete_port'
GET_PORT_CONF = 'get_port_conf'


class __Autonomy__(object):
    def __init__(self):
        self._buff = ""

    def write(self, out_stream):
        self._buff += out_stream

    def buff(self):
        return self._buff

    def flush(self):
        return


class NetworkRunner(object):
    """Object to invoke ansible_runner to call Ansible Networking
    Hold inventory and provide an interface for calling
    roles in Ansible Networking to manipulate switch configuration
    """

    def __init__(self, inventory=None):
        if inventory is not None:
            assert isinstance(inventory, Inventory)
        self.inventory = inventory or Inventory()

    def has_host(self, host):
        """Check if given host is in the inventory

        :param host: Name or ansible host of ```Host```
        :type host: String

        :returns: Boolean
        """
        for n, h in self.inventory.hosts.items():
            if h.ansible_host == host or n == host:
                return True
        return False

    def add_host(self, host):
        """Add host to inventory

        Adds a new ```Host``` instance to the current inventory
        object.  The value must be a value ```Host``` instance.

        :param host: A valid instance of ```Host```
        :type host: network_runner.models.inventory.hosts.Host

        :returns: None
        """
        assert isinstance(host, Host)
        self.inventory.hosts.add(host)

    def run(self, playbook):
        assert isinstance(playbook, Playbook)

        # invoke ansible networking via ansible runner
        result = ansible_runner.run(playbook=playbook.serialize(),
                                    inventory=self.inventory.serialize(),
                                    verbosity=True,
                                    settings={'pexpect_use_poll': False})

        # check for failure
        if result.status == 'failed' or \
                (result.stats and result.stats.get('failures', [])):
            raise exceptions.NetworkRunnerException(' '.join(result.stdout))

        return result

    def play(self, tasks_from, hosts=None, variables=None):
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
        play = pb.new(hosts=(hosts or ALL), gather_facts=False)

        task = play.tasks.new(action=IMPORT_ROLE)
        task.args = {'name': NETWORK_RUNNER, 'tasks_from': tasks_from}
        if variables:
            task.vars = variables

        return self.run(pb)

    def create_vlan(self, hostname, vlan_id, vlan_name=None, **kwargs):
        """Create VLAN.

        :param hostname: The name of the host in Ansible inventory.
        :param vlan_id: The VLAN's ID to create.
        :param vlan_name: The VLAN's name/description.
        """
        variables = {'vlan_id': vlan_id, 'vlan_name': vlan_name}
        variables.update(kwargs)
        return self.play(CREATE_VLAN, hostname, variables)

    def list_vlans(self, hostname, **kwargs):
        """List VLANs.

        :param hostname: The name of the host in Ansible inventory.
        """
        variables = kwargs
        return self.play(LIST_VLANS, hostname, variables)

    def delete_vlan(self, hostname, vlan_id, **kwargs):
        """Delete VLAN.

        :param hostname: The name of the host in Ansible inventory.
        :param vlan_id: The VLAN's ID to delete.
        """
        variables = {'vlan_id': vlan_id}
        variables.update(kwargs)
        return self.play(DELETE_VLAN, hostname, variables)

    def conf_access_port(self, hostname, port, vlan_id, **kwargs):
        """Configure access port on a vlan.

        :param hostname: The name of the host in Ansible inventory.
        :param port: The port to configure.
        :param vlan_id: The vlan_id to assign to the port.
                        An empty or None value will default to the
                        target device's default VLAN assignment. This
                        default is assigned in the ansible role.
        :param kwargs: used to pass platform specific parameters into
                       the ansible roles. For example immediate STP
                       fwding state is named different things on different
                       platforms.
        """
        variables = {'vlan_id': vlan_id, 'port_name': port,
                     'port_description': port}
        variables.update(kwargs)
        return self.play(CONF_ACCESS_PORT, hostname, variables)

    def conf_trunk_port(self, hostname, port, vlan_id,
                        trunked_vlans, **kwargs):
        """Configure trunk port w/ default vlan and optional additional vlans

        :param hostname: The name of the host in Ansible inventory.
        :param port: The port to configure.
        :param vlan_id: the default VLAN ID to assign to the port
                        An empty or None value will default to the
                        target device's default VLAN assignment. This
                        default is assigned in the ansible role.
        :param trunked_vlans: A list of VLAN IDs to add to the port in
                              addition to the default VLAN.
        :param kwargs: used to pass platform specific parameters into
                       the ansible roles. For example immediate STP
                       fwding state is named different things on different
                       platforms.
        """
        variables = {'vlan_id': vlan_id, 'port_name': port,
                     'port_description': port, 'trunked_vlans': trunked_vlans}
        variables.update(kwargs)
        return self.play(CONF_TRUNK_PORT, hostname, variables)

    def add_trunk_vlan(self, hostname, port, vlan_id, **kwargs):
        """Add VLAN to trunk port.

        :param hostname: The name of the host in Ansible inventory.
        :param port: The port to configure.
        :param vlan_id: The VLAN's ID to delete.
        """
        variables = {'vlan_id': vlan_id, 'port_name': port}
        variables.update(kwargs)
        return self.play(ADD_TRUNK_VLAN, hostname, variables)

    def delete_trunk_vlan(self, hostname, port, vlan_id, **kwargs):
        """Delete VLAN.

        :param hostname: The name of the host in Ansible inventory.
        :param port: The port to configure.
        :param vlan_id: The VLAN's ID to delete.
        """
        variables = {'vlan_id': vlan_id, 'port_name': port}
        variables.update(kwargs)
        return self.play(DELETE_TRUNK_VLAN, hostname, variables)

    def delete_port(self, hostname, port, **kwargs):
        """Delete port configuration.

        :param hostname: The name of the host in Ansible inventory.
        :param port: The port to configure.
        """
        variables = {'port_name': port}
        variables.update(kwargs)
        return self.play(DELETE_PORT, hostname, variables)

    def get_port_conf(self, hostname, port, **kwargs):
        """Get port configuration.

        :param hostname: The name of the host in Ansible inventory.
        :param port: The port to get configuration.
        """
        variables = {'port_name': port}
        variables.update(kwargs)
        current = sys.stdout
        a = __Autonomy__()
        sys.stdout = a
        self.play(GET_PORT_CONF, hostname, variables)
        sys.stdout = current
        return print(format_port_config(a.buff(),
                     self.inventory.hosts[hostname].ansible_network_os))
