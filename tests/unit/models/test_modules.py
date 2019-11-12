# Copyright (c) 2019 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import os

import pytest

from network_runner.models import modules
from network_runner.models.playbook import Task


def test_importrole():
    with pytest.raises(ValueError):
        modules.ImportRole()

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        os.pardir, os.pardir,
                        "etc/ansible/roles")
    os.environ['ANSIBLE_ROLES_PATH'] = path

    obj = modules.ImportRole(name='network-runner')

    assert isinstance(obj, modules.ImportRole)
    assert obj.name == 'network-runner'
    assert obj.tasks_from is None

    obj = modules.ImportRole(name='network-runner', tasks_from='tasks')

    assert isinstance(obj, modules.ImportRole)
    assert obj.name == 'network-runner'
    assert obj.tasks_from == 'tasks'

    task = obj.to_task()

    assert isinstance(task, Task)
    assert task.action == 'import_role'
    assert task.args['name'] == 'network-runner'
    assert task.args['tasks_from'] == 'tasks'
