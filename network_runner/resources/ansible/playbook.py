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

from network_runner.resources import Entity, Collection
from network_runner.resources.attributes import Attribute


class Task(Entity):

    _name = Attribute(serialize='present')
    _module = Attribute(required=True)
    _args = Attribute(type='dict')
    _vars = Attribute(type='dict')
    _when = Attribute(serialize='present')
    _connection = Attribute(serialize='present')

    def serialize(self):
        obj = super(Task, self).serialize()
        mod = obj.pop('module')
        args = obj.pop('args', {})
        assert isinstance(args, dict)
        obj[mod] = args
        return obj

    def deserialize(self, ds):
        obj = {}
        for key in self._attributes:
            if key in ds:
                value = ds.pop(key)
                obj[key] = value

        assert len(ds) == 1, "unknown key/value in task"

        for key, value in iteritems(ds):
            obj['module'] = key
            obj['args'] = value

        super(Task, self).deserialize(obj)


class Tasks(Collection):

    __item_class__ = Task


class Play(Entity):

    _name = Attribute(serialize='present')
    _hosts = Attribute(default='all')
    _gather_facts = Attribute(type='bool', serialize='present')
    _connection = Attribute(serialize='present')
    _tasks = Attribute(cls=Tasks)


class Playbook(Collection):

    __item_class__ = Play
