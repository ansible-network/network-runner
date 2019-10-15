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
import json

from six import with_metaclass, iteritems

from network_runner.types.attrs import Attribute
from network_runner.types.attrs import SERIALIZE_WHEN_ALWAYS
from network_runner.types.attrs import SERIALIZE_WHEN_NEVER
from network_runner.helpers import isvalidattrname


class BaseMeta(type):

    def __new__(cls, name, parents, dct):
        dct['_attr_names'] = set()

        def _create_attrs(attr_dct):
            for attr_name in attr_dct:
                value = attr_dct[attr_name]
                if isinstance(value, Attribute):
                    name = attr_name[1:]
                    isvalidattrname(name)
                    dct['_attr_names'].add(name)

        # process parents first to allow more specific overrides
        for parent in parents:
            _create_attrs(parent.__dict__)

        _create_attrs(dct)

        dct['_attr_names'] = frozenset(dct['_attr_names'])

        return super(BaseMeta, cls).__new__(cls, name, parents, dct)


class Object(with_metaclass(BaseMeta)):

    def __init__(self, **kwargs):
        for item in self._attr_names:
            setattr(self, item, kwargs.get(item))

    def __repr__(self):
        return json.dumps(self.serialize())

    def __setattr__(self, key, value):
        if key in self._attr_names:
            value = getattr(self, '_{}'.format(key))(value)

        elif key in dir(self):
            attr = getattr(self, key)
            if isinstance(attr, Attribute):
                raise AttributeError("attribute '{}' is read only".format(key))

        elif not key.startswith('_'):
            raise AttributeError("'{}' object has no attribute '{}'".format(
                self.__class__.__name__, key))

        self.__dict__[key] = value

    def __delattr__(self, key):
        attr = getattr(self, '_{}'.format(key), None)

        if attr and attr.required is True:
            raise ValueError('required attributes cannot be deleted')

        elif not attr and key in dir(self):
            raise AttributeError("cannot delete attribute '{}'".format(key))

        else:
            self.__dict__[key] = attr()

    def __eq__(self, other):
        return self.serialize() == other.serialize()

    def __neq__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        return self.__eq__(other)

    def __hash__(self):
        return hash(self.serialize())

    def __sizeof__(self):
        return len(json.dumps(self.serialize()))

    def __getstate__(self):
        obj = {}
        for item in self._attr_names:
            attr = getattr(self, '_{}'.format(item))
            value = getattr(self, item)

            if value is not None and \
               attr.serialize_when < SERIALIZE_WHEN_NEVER or \
               attr.serialize_when == SERIALIZE_WHEN_ALWAYS:
                if hasattr(value, 'serialize'):
                    obj[item] = value.serialize()
                else:
                    obj[item] = value

        return obj

    serialize = __getstate__

    def __setstate__(self, ds):
        assert isinstance(ds, dict), "argument must be of type 'dict'"
        for key, value in iteritems(ds):
            attr = getattr(self, key)
            if hasattr(attr, 'deserialize'):
                attr.deserialize(value)
            else:
                setattr(self, key, value)

    deserialize = __setstate__
