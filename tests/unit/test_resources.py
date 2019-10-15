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

from network_runner.resources.inventory import Inventory
from network_runner.resources.inventory import Host
from network_runner.resources.inventory import Child
from network_runner.resources.playbook import Playbook
from network_runner.resources.playbook import Play
from network_runner.resources.playbook import Task

EMPTY_INV = {'all': {'hosts': {}, 'vars': {}, 'children': {}}}
TEST_HOST = {'name': 'test'}
EMPTY_CHILD = {'hosts': {}, 'vars': {}}
EMPTY_PLAYBOOK = []
EMPTY_PLAY = {'hosts': 'all', 'tasks': []}
NOOP_TASK = {'noop': {}, 'vars': {}}


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
        host = Host(name='test',
                    ansible_host='testhost',
                    ansible_user='testuser',
                    ansible_password='testpass',
                    ansible_network_os='openvswitch')

        self.assertEqual(host.name, 'test')
        self.assertEqual(host.ansible_host, 'testhost')
        self.assertEqual(host.ansible_user, 'testuser')
        self.assertEqual(host.ansible_password, 'testpass')
        self.assertEqual(host.ansible_network_os, 'openvswitch')

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
        task = Task(module='noop')
        self.assertEqual(type(task), Task)

        serialized_task = task.serialize()
        self.assertEqual(serialized_task, NOOP_TASK)

        task.deserialize(NOOP_TASK)
        self.assertEqual(task, Task(module='noop'))
