# Copyright (c) 2018 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from . import base

from network_runner.models.inventory import Inventory
from network_runner.models.inventory import Host
from network_runner.models.inventory import Child
from network_runner.models.playbook import Playbook
from network_runner.models.playbook import Play
from network_runner.models.playbook import Task


EMPTY_INV = {'all': {'hosts': {}, 'vars': {}, 'children': {}}}
TEST_HOST = {'name': 'test'}
EMPTY_CHILD = {'hosts': {}, 'vars': {}}
EMPTY_PLAYBOOK = []
EMPTY_PLAY = {'hosts': 'all'}
NOOP_TASK = {'action': 'noop', 'args': {}}


class TestResourcesInventory(base.NetworkRunnerTestCase):

    def test_empty_inventory(self):
        inventory = Inventory()
        self.assertEqual(type(inventory), Inventory)

        serialized_inv = inventory.serialize()
        self.assertEqual(serialized_inv, EMPTY_INV)

        inventory.deserialize(EMPTY_INV)
        self.assertEqual(inventory, Inventory())

    def test_empty_host(self):
        host = Host(name='test')
        self.assertEqual(type(host), Host)

        serialized_host = host.serialize()
        self.assertEqual(serialized_host, TEST_HOST)

        host.deserialize(TEST_HOST)
        self.assertEqual(host, Host(name='test'))

    def test_host_attrs(self):
        host = Host(ansible_host='testhost',
                    ansible_user='testuser',
                    ansible_password='testpass',
                    ansible_network_os='openvswitch')

        self.assertEqual(host.ansible_host, 'testhost')
        self.assertEqual(host.ansible_user, 'testuser')
        self.assertEqual(host.ansible_password, 'testpass')
        self.assertEqual(host.ansible_ssh_pass, 'testpass')
        self.assertEqual(host.ansible_network_os, 'openvswitch')

    def test_host_attrs_alias(self):
        host = Host(ansible_ssh_pass='testpass')

        self.assertEqual(host.ansible_password, 'testpass')
        self.assertEqual(host.ansible_ssh_pass, 'testpass')

    def test_host_vars(self):
        host = Host(name='test')
        host.vars['testvar'] = 'testing123'
        self.assertEqual(host.vars['testvar'], 'testing123')

    def test_host_invalid_ansible_network_os(self):
        self.assertRaises(AttributeError, Host, name='test',
                          ansible_network_os='notreal')

    def test_empty_child(self):
        child = Child()
        self.assertEqual(type(child), Child)

        serialized_child = child.serialize()
        self.assertEqual(serialized_child, EMPTY_CHILD)

        child.deserialize(EMPTY_CHILD)
        self.assertEqual(child, Child())

    def test_host_vars_kwargs(self):
        host = Host(ansible_host='testhost',
                    key1='value1',
                    key2='value2')

        self.assertEqual(host.ansible_host, 'testhost')
        self.assertEqual(host.vars, {'key1': 'value1', 'key2': 'value2'})

    def test_child_vars_kwargs(self):
        child = Child(key1='value1',
                      key2='value2')

        self.assertEqual(child.vars, {'key1': 'value1', 'key2': 'value2'})


class TestResourcesAnsiblePlaybook(base.NetworkRunnerTestCase):

    def test_empty_playbook(self):
        playbook = Playbook()
        self.assertEqual(type(playbook), Playbook)

        serialized_playbook = playbook.serialize()
        self.assertEqual(serialized_playbook, EMPTY_PLAYBOOK)

        # TODO(radez) why is [] != [] ???
        playbook.deserialize(EMPTY_PLAYBOOK)
        self.assertEqual(playbook, Playbook())

    def test_empty_play(self):
        play = Play()
        self.assertEqual(type(play), Play)

        serialized_play = play.serialize()
        self.assertEqual(serialized_play, EMPTY_PLAY)

        play.deserialize(EMPTY_PLAY)
        self.assertEqual(play, Play())

    def test_noop_task(self):
        task = Task(action='noop')
        self.assertEqual(type(task), Task)

        serialized_task = task.serialize()
        self.assertEqual(serialized_task, NOOP_TASK)

        task.deserialize(NOOP_TASK)
        self.assertEqual(task, Task(action='noop'))


def test_serialize_deserialize():
    pb = Playbook()
    p = pb.new()
    p.tasks.new(action='noop', args={'foo': 'bar'})
    ds = pb.serialize()
    newpb = Playbook()
    newpb.deserialize(ds)
    assert pb.serialize() == newpb.serialize()
