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
from network_runner.types.objects import Object
from network_runner.types.attrs import String, Dict, TypedDict
from network_runner.types.attrs import SERIALIZE_WHEN_PRESENT
from network_runner.types.attrs import SERIALIZE_WHEN_NEVER
from network_runner.types.validators import ChoiceValidator


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
NETWORK_OS_VALIDATOR = ChoiceValidator(choices=(PROVIDERS))


class Host(Object):

    name = String(
        required=True
    )

    ansible_host = String(
        serialize_when=SERIALIZE_WHEN_PRESENT
    )

    ansible_user = String(
        serialize_when=SERIALIZE_WHEN_PRESENT
    )

    ansible_password = String(
        serialize_when=SERIALIZE_WHEN_PRESENT,
        aliases=('ansible_ssh_pass',)
    )

    ansible_network_os = String(
        serialize_when=SERIALIZE_WHEN_PRESENT,
        validators=(NETWORK_OS_VALIDATOR,)
    )

    vars = Dict(
        serialize_when=SERIALIZE_WHEN_NEVER
    )

    def __init__(self, **kwargs):
        hostvars = {}
        for item in set(kwargs).difference(self._attributes):
            hostvars[item] = kwargs[item]
            kwargs.pop(item)

        if 'vars' not in kwargs:
            kwargs['vars'] = {}
        kwargs['vars'].update(hostvars)

        super(Host, self).__init__(**kwargs)

    def serialize(self):
        obj = super(Host, self).serialize()
        obj['name'] = self.name
        obj.update(self.vars)
        return obj

    def deserialize(self, ds):
        assert isinstance(ds, dict)
        obj = {}
        for name in self._attributes:
            obj[name] = ds.pop(name, None)
        super(Host, self).deserialize(obj)
        self.vars.update(ds)


class Child(Object):

    name = String(
        serialize_when=SERIALIZE_WHEN_NEVER
    )

    hosts = TypedDict(
        item_class=Host,
        item_key='name'
    )

    vars = Dict()

    def __init__(self, **kwargs):
        childvars = {}
        for item in set(kwargs).difference(self._attributes):
            childvars[item] = kwargs[item]
            kwargs.pop(item)

        if 'vars' not in kwargs:
            kwargs['vars'] = {}
        kwargs['vars'].update(childvars)

        super(Child, self).__init__(**kwargs)


class Inventory(Object):

    hosts = TypedDict(
        item_class=Host,
        item_key='name'
    )

    children = TypedDict(
        item_class=Child,
        item_key='name'
    )

    vars = Dict()

    def serialize(self):
        obj = super(Inventory, self).serialize()
        return {'all': obj}

    def deserialize(self, obj):
        super(Inventory, self).deserialize(obj['all'])
