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
from six import iteritems

from network_runner.types.objects import Object
from network_runner.types.attrs import Attribute
from network_runner.types.attrs import Container
from network_runner.types.containers import Index

from network_runner.types.attrs import SERIALIZE_WHEN_PRESENT


class Base(object):

    _connection = Attribute(serialize_when=SERIALIZE_WHEN_PRESENT)


class Task(Base, Object):

    _name = Attribute(serialize_when=SERIALIZE_WHEN_PRESENT)
    _module = Attribute(required=True)
    _args = Attribute(type='dict')
    _vars = Attribute(type='dict', serialize_when=SERIALIZE_WHEN_PRESENT)
    _when = Attribute(serialize_when=SERIALIZE_WHEN_PRESENT)

    def serialize(self):
        obj = super(Task, self).serialize()
        module = obj.pop('module')
        args = obj.pop('args')
        obj[module] = args
        return obj

    def deserialize(self, ds):
        obj = {}
        for name in self._attr_names:
            if name in ds:
                value = ds.pop(name)
                obj[name] = value

        assert len(ds) == 1, "unknown key/value in task"

        for key, value in iteritems(ds):
            obj['module'] = key
            obj['args'] = value

        super(Task, self).deserialize(obj)


class Play(Base, Object):

    _name = Attribute(
        serialize_when=SERIALIZE_WHEN_PRESENT
    )

    _hosts = Attribute(
        default='all'
    )

    _gather_facts = Attribute(
        type='bool',
        serialize_when=SERIALIZE_WHEN_PRESENT
    )

    _tasks = Container(
        type='index',
        cls=Task
    )


class Playbook(Index):

    def __init__(self):
        super(Playbook, self).__init__(Play)
