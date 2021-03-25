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
from network_runner.resources import Entity, KeyedCollection
from network_runner.resources.attributes import Attribute
from network_runner.resources.validators import ChoiceValidator

# Build the list of platform modules in the role providers directory
import os
RP_DEFAULT = '/usr/share/ansible/roles:/etc/ansible/roles:etc/ansible/roles'
ROLE_PATH = os.environ.get('ANSIBLE_ROLES_PATH', RP_DEFAULT).split(':')
PROVIDERS = []
for i in ROLE_PATH:
    net_runner_path = os.path.sep.join([i, 'network-runner'])
    if os.path.exists(net_runner_path):
        provider_path = os.path.sep.join([net_runner_path, 'providers'])
        PROVIDERS.extend(os.listdir(provider_path))
        break  # assume one installation of network-runner

# Create a validator from the providers list
net_os_validator = ChoiceValidator(choices=(PROVIDERS))


class Host(Entity):

    _name = Attribute(required=True, serialize='never')
    _ansible_host = Attribute(serialize='present')
    _ansible_user = Attribute(serialize='present')
    _ansible_ssh_pass = Attribute(serialize='present')
    _ansible_network_os = Attribute(serialize='present',
                                    validator=net_os_validator)

    def __init__(self, *args, **kwargs):
        self._vars = dict()
        super(Host, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        self._vars[key] = value

    def __getitem__(self, key):
        return self._vars[key]

    def serialize(self):
        obj = super(Host, self).serialize()
        obj['name'] = self.name
        obj.update(self._vars)
        return obj

    def deserialize(self, ds):
        assert isinstance(ds, dict)
        obj = {}
        for key in self._attributes:
            obj[key] = ds.pop(key, None)
        super(Host, self).deserialize(obj)
        self._vars.update(ds)


class Hosts(KeyedCollection):

    __item_class__ = Host
    __item_key__ = 'name'
