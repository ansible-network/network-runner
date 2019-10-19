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
from network_runner.types.attrs import Attribute
from network_runner.types.attrs import Container
from network_runner.types.attrs import SERIALIZE_WHEN_PRESENT
from network_runner.types.attrs import SERIALIZE_WHEN_NEVER
from network_runner.types.validators import ChoiceValidator


NETWORK_OS_VALIDATOR = ChoiceValidator(
    choices=('cumulus', 'dellos10', 'eos', 'junos', 'nxos', 'openvswitch')
)


class Host(Object):

    name = Attribute(
        required=True,
        serialize_when=SERIALIZE_WHEN_NEVER
    )

    ansible_host = Attribute(
        serialize_when=SERIALIZE_WHEN_PRESENT
    )

    ansible_user = Attribute(
        serialize_when=SERIALIZE_WHEN_PRESENT
    )

    ansible_password = Attribute(
        serialize_when=SERIALIZE_WHEN_PRESENT
    )

    ansible_network_os = Attribute(
        serialize_when=SERIALIZE_WHEN_PRESENT,
        validator=NETWORK_OS_VALIDATOR
    )

    vars = Attribute(
        type='dict',
        serialize_when=SERIALIZE_WHEN_NEVER
    )

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

    name = Attribute(
        serialize_when=SERIALIZE_WHEN_NEVER
    )

    hosts = Container(
        type='map',
        cls=Host,
        item_key='name'
    )

    vars = Attribute(
        type='dict'
    )


class Inventory(Object):

    hosts = Container(
        type='map',
        cls=Host,
        item_key='name'
    )

    children = Container(
        type='map',
        cls=Child,
        item_key='name'
    )

    vars = Attribute(
        type='dict'
    )

    def serialize(self):
        obj = super(Inventory, self).serialize()
        return {'all': obj}

    def deserialize(self, obj):
        super(Inventory, self).deserialize(obj['all'])
