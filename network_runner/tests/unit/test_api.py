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

import mock

from network_runner import exceptions
from network_runner.resources.ansible import playbook
from network_runner.resources.inventory.hosts import Host
from network_runner.api import NetworkRunner
from network_runner.tests.unit import base


class TestAddHost(base.BaseTestCase):

    def test_add_host(self):
        host = Host(name='test')
        api = NetworkRunner()
        assert 'test' not in api.inventory.hosts
        api.add_host(host)
        assert 'test' in api.inventory.hosts

    def test_add_host_fail(self):
        api = NetworkRunner()
        assert 'test' not in api.inventory.hosts
        with self.assertRaises(AssertionError):
            api.add_host(None)


class TestCreateDeleteVlan(base.NetworkRunnerTestCase):

    @mock.patch('network_runner.api.NetworkRunner.run')
    def test_create_vlan(self, m_run_task):
        self.net_runr.create_vlan(self.testhost, self.testvlan)
        m_run_task.assert_called_once()

    @mock.patch('network_runner.api.NetworkRunner.run')
    def test_delete_vlan(self, m_run_task):
        self.net_runr.delete_vlan(self.testhost, self.testvlan)
        m_run_task.assert_called_once()


@mock.patch('network_runner.api.ansible_runner')
class TestRun(base.NetworkRunnerTestCase):

    def test_run(self, m_ans_runner):
        m_result = m_ans_runner.run.return_value
        m_result.stats = {'failures': []}

        self.net_runr.run(playbook.Playbook())

        m_ans_runner.run.assert_called_once()

    def test_run_task_failures(self, m_ans_runner):
        m_result = m_ans_runner.run.return_value
        m_result.status = 'failed'
        self.assertRaises(exceptions.NetworkRunnerException,
                          self.net_runr.run,
                          playbook.Playbook())

        m_result.status = ''
        m_result.stats = {'failures': ['I got some failure']}
        self.assertRaises(exceptions.NetworkRunnerException,
                          self.net_runr.run,
                          playbook.Playbook())


@mock.patch('network_runner.api.NetworkRunner.run')
class TestConfAccessPort(base.NetworkRunnerTestCase):

    def test_assign_access_port(self, m_run_task):
        self.net_runr.conf_access_port(self.testhost,
                                       self.testport,
                                       self.testvlan)
        m_run_task.assert_called_once()

    def test_remove_access_port(self, m_run_task):
        self.net_runr.delete_port(self.testhost, self.testport)

        m_run_task.assert_called_once()

    def test_remove_access_port_raises(self, m_run_task):
        m_run_task.side_effect = exceptions.NetworkRunnerException('test')
        self.assertRaises(exceptions.NetworkRunnerException,
                          self.net_runr.delete_port,
                          self.testhost, self.testport)


@mock.patch('network_runner.api.NetworkRunner.run')
class TestConfTrunkPort(base.NetworkRunnerTestCase):

    def test_assign_trunk_port(self, m_run_task):
        self.net_runr.conf_trunk_port(self.testhost,
                                      self.testport,
                                      self.testvlan,
                                      trunked_vlans=self.testvlans)

        m_run_task.assert_called_once()

    def test_remove_trunk_port(self, m_run_task):
        self.net_runr.delete_port(self.testhost, self.testport)

        m_run_task.assert_called_once()

    def test_remove_trunk_port_raises(self, m_run_task):
        m_run_task.side_effect = exceptions.NetworkRunnerException('test')
        self.assertRaises(exceptions.NetworkRunnerException,
                          self.net_runr.delete_port,
                          self.testhost, self.testport)
