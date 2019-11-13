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
import re

import pytest

from network_runner import helpers


def test_isvalidattrname():
    with pytest.raises(ValueError):
        helpers.isvalidattrname('import')

    with pytest.raises(ValueError):
        helpers.isvalidattrname('0test')

    helpers.isvalidattrname('test')


def test_get_ansible_role_paths():
    resp = helpers.get_ansible_role_paths()
    assert resp


def test_ansible_version():
    resp = helpers.get_ansible_version()
    match = re.match(helpers.to_bytes("\\d+\\.\\d+\\.\\d+"), resp)
    assert match is not None


def test_get_role_path():
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        os.pardir, os.pardir,
                        "etc/ansible/roles")

    os.environ['ANSIBLE_ROLES_PATH'] = path
    resp = helpers.get_role_path('network-runner')
    expected = os.path.abspath(os.path.join(path, 'network-runner'))

    assert helpers.to_text(resp) == expected


def test_to_bytes():
    assert helpers.to_bytes("test") == b"test"
    assert helpers.to_bytes(u"test") == b"test"
    assert helpers.to_bytes(b"test") == b"test"


def test_to_text():
    assert helpers.to_text(b"test") == "test"
    assert helpers.to_text(u"test") == "test"
    assert helpers.to_text("test") == "test"


def test_to_list():
    assert helpers.to_list(None) == []
    assert helpers.to_list('test') == ['test']
    assert helpers.to_list(['test']) == ['test']
    assert helpers.to_list(('test',)) == ['test']
    assert helpers.to_list(set(['test'])) == ['test']
