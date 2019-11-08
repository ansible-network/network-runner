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
        dct['_attributes'] = {}

        def _create_attrs(attr_dct):
            for attr_name in attr_dct:
                attr = attr_dct[attr_name]
                if isinstance(attr, Attribute):
                    attr.name = attr_name

                    isvalidattrname(attr_name)
                    dct['_attributes'][attr_name] = attr

                    removed = set()

                    for entry in list(attr.aliases):
                        if entry not in attr_dct:
                            isvalidattrname(entry)
                            dct['_attributes'][entry] = attr
                        elif entry in attr_dct:
                            removed.add(entry)

                    attr.aliases = tuple(set(attr.aliases).difference(removed))

        # process parents first to allow more specific overrides
        for parent in parents:
            _create_attrs(parent.__dict__)

        _create_attrs(dct)

        return super(BaseMeta, cls).__new__(cls, name, parents, dct)


class Object(with_metaclass(BaseMeta)):

    def __init__(self, **kwargs):
        for key, value in iteritems(kwargs):
            attr = self._attributes[key]
            if key == attr.name:
                setattr(self, key, value)
            elif key in attr.aliases:
                setattr(self, attr.name, value)

        for key, attr in iteritems(self._attributes):
            value = getattr(self, key, None)
            if not value or isinstance(value, Attribute):
                setattr(self, key, attr.default)

    def __repr__(self):
        return json.dumps(self.serialize())

    def __setattr__(self, key, value):
        if key in self._attributes:
            attr = self._attributes[key]
            value = attr(value)

            if attr.name != key:
                self.__dict__[attr.name] = value

            for item in attr.aliases:
                if item != key:
                    self.__dict__[item] = value

        elif key in dir(self):
            attr = getattr(self, key)
            if isinstance(attr, Attribute):
                raise AttributeError("attribute '{}' is read only".format(key))

        elif not key.startswith('_'):
            raise AttributeError("'{}' object has no attribute '{}'".format(
                self.__class__.__name__, key))

        self.__dict__[key] = value

    def __delattr__(self, key):
        attr = self._attributes.get(key)

        if attr and attr.required is True:
            raise ValueError('required attributes cannot be deleted')

        elif not attr and key in dir(self):
            raise AttributeError("cannot delete attribute '{}'".format(key))

        else:
            self.__dict__[key] = attr()

            if attr.name != key:
                self.__dict__[attr.name] = attr()

            for item in attr.aliases:
                self.__dict__[item] = attr()

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
        for item, attr in iteritems(self._attributes):
            value = getattr(self, item)

            if attr.attrtype in ('dict', 'list'):
                if value and attr.serialize_when != SERIALIZE_WHEN_NEVER or \
                    attr.serialize_when == SERIALIZE_WHEN_ALWAYS:

                    if hasattr(value, 'serialize'):
                        obj[item] = value.serialize()
                    else:
                        obj[item] = value

            elif value is not None and \
                attr.serialize_when < SERIALIZE_WHEN_NEVER:

                if hasattr(value, 'serialize'):
                    obj[item] = value.serialize()
                else:
                    obj[item] = value

        return obj

    serialize = __getstate__

    def __setstate__(self, ds):
        assert isinstance(ds, dict), "argument must be of type 'dict'"
        for key, value in iteritems(ds):
            attr = self._attributes[key]
            if hasattr(attr, 'deserialize'):
                attr.deserialize(value)
            else:
                setattr(self, key, value)

    deserialize = __setstate__
