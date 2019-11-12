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

from network_runner.bindings.role import load
from network_runner.bindings.role import get_role_bindings
from network_runner.models.playbook import Task
from network_runner.types.objects import Object
from network_runner.exceptions import NetworkRunnerException


def test_role_fail():
    with pytest.raises(TypeError):
        load()


def test_role_create(datadir):
    os.environ['ANSIBLE_ROLES_PATH'] = str(datadir)
    obj = load(role_name='network-runner')
    assert obj.__module__ == "network_runner.bindings.role"
    assert obj.__class__.__name__ == 'network_runner'


def test_uses_reserved_python_name(datadir):
    os.environ['ANSIBLE_ROLES_PATH'] = str(datadir)
    with pytest.raises(ValueError):
        load(role_name='python_reserved')


def test_role_create_model(datadir):
    os.environ['ANSIBLE_ROLES_PATH'] = str(datadir)
    role = load(role_name='network-runner')
    obj = role.new('vlan', vlan_id=1)
    assert isinstance(obj, Object)
    assert obj.vlan_id == 1
    assert obj.vlan_name is None


def test_role_has_actions(datadir):
    os.environ['ANSIBLE_ROLES_PATH'] = str(datadir)
    role = load(role_name='network-runner')
    assert hasattr(role, 'create_vlan')
    assert hasattr(role, 'delete_vlan')


def test_role_run_action(datadir):
    os.environ['ANSIBLE_ROLES_PATH'] = str(datadir)
    role = load(role_name='network-runner')
    task = role.delete_vlan(vlan_id=1)
    assert isinstance(task, Task)


def test_role_types_action(datadir):
    os.environ['ANSIBLE_ROLES_PATH'] = str(datadir)

    role = load(role_name='test-action')

    role.method(string='string', integer=1, boolean=True, alist=[], adict={},
                model=role.new('model', name='test'))

    with pytest.raises(AttributeError):
        role.method(unknown='arg')

    with pytest.raises(Exception):
        role.method(valid='three')

    with pytest.raises(ValueError):
        role.method(adict="test")

    with pytest.raises(ValueError):
        role.method(model="foo")


def test_get_role_bindings(datadir):
    resp = get_role_bindings(datadir / 'network-runner')
    assert resp is not None

    with pytest.raises(NetworkRunnerException):
        get_role_bindings('/tmp')
