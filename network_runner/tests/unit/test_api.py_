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

from networking_ansible import exceptions
from networking_ansible.tests.unit import base


class TestCreateDeleteNetwork(base.NetworkingAnsibleTestCase):

    @mock.patch('networking_ansible.api'
                '.NetworkingAnsible._run_task')
    def test_create_vlan(self, mock_run_task):
        self.mech.ansnet.create_vlan(self.testhost, self.testsegid)
        mock_run_task.assert_called_once_with('create_vlan',
                                              self.testhost,
                                              vlan_id=self.testsegid)

    @mock.patch('networking_ansible.api'
                '.NetworkingAnsible._run_task')
    def test_delete_vlan(self, mock_run_task):
        self.mech.ansnet.delete_vlan(self.testhost, self.testsegid)
        mock_run_task.assert_called_once_with('delete_vlan',
                                              self.testhost,
                                              vlan_id=self.testsegid)


@mock.patch('networking_ansible.api.ansible_runner')
class TestRunTask(base.NetworkingAnsibleTestCase):
    def test_run_task_no_switchport(self, mock_ans_runner):
        mock_result = mock_ans_runner.run.return_value
        mock_result.stats = {'failures': []}

        self.mech.ansnet._run_task('fake_task',
                                   self.testhost,
                                   vlan_name='test_vlan')
        # Assert switch_port is not set
        self.assertNotIn('port',
                         mock_ans_runner.run.call_args[1]['playbook'][0]
                                                      ['tasks'][0]['vars']
                         )
        # Assert switch_port is not set
        self.assertNotIn('port_description',
                         mock_ans_runner.run.call_args[1]['playbook'][0]
                                                      ['tasks'][0]['vars']
                         )

    def test_run_task_w_switchport(self, mock_ans_runner):
        mock_result = mock_ans_runner.run.return_value
        mock_result.stats = {'failures': []}

        self.mech.ansnet._run_task('fake_task',
                                   self.testhost,
                                   self.testport,
                                   self.testsegid)
        # Assert switch_port is set
        self.assertEqual(
            self.testport,
            mock_ans_runner.run.call_args[1]['playbook'][0]['tasks']
                                         [0]['vars']['port_name'])
        # Assert switch_port is set
        self.assertEqual(
            self.testport,
            mock_ans_runner.run.call_args[1]['playbook'][0]['tasks']
                                         [0]['vars']['port_description'])

    def test_run_task_failures(self, mock_ans_runner):
        mock_result = mock_ans_runner.run.return_value
        mock_result.status = 'failed'
        self.assertRaises(exceptions.AnsibleRunnerException,
                          self.mech.ansnet._run_task,
                          'fake_task',
                          self.testhost,
                          self.testsegid,
                          'fake_switchport')

        mock_result.status = ''
        mock_result.stats = {'failures': ['I got some failure']}
        self.assertRaises(exceptions.AnsibleRunnerException,
                          self.mech.ansnet._run_task,
                          'fake_task',
                          self.testhost,
                          'fake_switchport',
                          self.testsegid)


@mock.patch('networking_ansible.api'
            '.NetworkingAnsible._run_task')
class TestVlanAccessPort(base.NetworkingAnsibleTestCase):

    def test_assign_vlan_access_port(self, mock_run_task):
        self.mech.ansnet.update_access_port(self.testhost,
                                            self.testport,
                                            self.testsegid)
        mock_run_task.assert_called_once_with('update_access_port',
                                              self.testhost,
                                              self.testport,
                                              self.testsegid)

    def test_remove_vlan_access_port(self, mock_run_task):
        self.mech.ansnet.delete_port(self.testhost, self.testport)
        mock_run_task.assert_called_once_with('delete_port',
                                              self.testhost,
                                              self.testport)

    def test_remove_vlan_access_port_raises(self, mock_run_task):
        mock_run_task.side_effect = exceptions.AnsibleRunnerException('test')
        self.assertRaises(exceptions.AnsibleRunnerException,
                          self.mech.ansnet.delete_port,
                          self.testhost, self.testport)
