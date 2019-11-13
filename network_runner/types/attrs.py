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
from copy import deepcopy
from unicodedata import normalize

from six import PY2

from network_runner.types.containers import IndexContainer
from network_runner.types.containers import MapContainer
from network_runner.types.validators import TypeValidator
from network_runner.types.validators import RequiredValueValidator


SERIALIZE_WHEN_ALWAYS = 0
SERIALIZE_WHEN_PRESENT = 1
SERIALIZE_WHEN_NEVER = 2


class Attribute(object):

    def __init__(self, type, name=None, default=None, required=None,
                 validators=None, serialize_when=None, aliases=None):

        self.type = type
        self.name = name
        self.default = default
        self.validators = validators or set()
        self.aliases = aliases or ()
        self.serialize_when = serialize_when or SERIALIZE_WHEN_ALWAYS

        try:
            self.validators = set(self.validators)
        except Exception:
            raise AttributeError("validators must be iterable")

        if serialize_when is not None:
            if serialize_when not in (0, 1, 2):
                raise ValueError("invalid value for serialize_when")

        self.validators.add(TypeValidator(self.type))

        if required:
            self.validators.add(RequiredValueValidator())
            if self.serialize_when > 0:
                raise AttributeError(
                    "required attributes must always be serialized"
                )

        if self.default is not None:
            for item in self.validators:
                item(self.default)

    def __call__(self, value):
        value = value if value is not None else self.default
        for item in self.validators:
            item(value)
        return deepcopy(value)


class String(Attribute):

    def __init__(self, **kwargs):
        super(String, self).__init__(type=str, **kwargs)

    def __call__(self, value):
        if PY2 and isinstance(value, unicode):
            value = normalize('NFKD', value).encode('ascii', 'ignore')
        return super(String, self).__call__(value)


class Integer(Attribute):

    def __init__(self, *args, **kwargs):
        return super(Integer, self).__init__(type=int, **kwargs)


class Boolean(Attribute):

    def __init__(self, *args, **kwargs):
        return super(Boolean, self).__init__(type=bool, **kwargs)


class List(Attribute):

    def __init__(self, **kwargs):
        if kwargs.get('default') is None:
            kwargs['default'] = []
        super(List, self).__init__(type=list, **kwargs)


class Dict(Attribute):

    def __init__(self, **kwargs):
        if kwargs.get('default') is None:
            kwargs['default'] = {}
        super(Dict, self).__init__(type=dict, **kwargs)


class Object(Attribute):

    def __init__(self, type, **kwargs):
        if kwargs.get('default') is None:
            kwargs['default'] = type()
        kwargs['type'] = type
        super(Object, self).__init__(**kwargs)


class Map(Attribute):

    def __init__(self, cls, item_key=None, **kwargs):
        self.cls = cls
        if kwargs.get('default') is None:
            kwargs['default'] = MapContainer(self.cls)
        super(Map, self).__init__(type=MapContainer, **kwargs)

    def __call__(self, value):
        if isinstance(value, dict):
            obj = MapContainer(self.cls)
            obj.deserialize(value)
            value = obj
        return super(Map, self).__call__(value)


class Index(Attribute):

    def __init__(self, cls, **kwargs):
        self.cls = cls
        if kwargs.get('default') is None:
            kwargs['default'] = IndexContainer(self.cls)
        super(Index, self).__init__(type=IndexContainer, **kwargs)

    def __call__(self, value):
        # because a Index is serialialized as a list object, the
        # deserialization process will attempt to pass a native list into the
        # this method.  this will attempt to recreate the Index object
        if isinstance(value, list):
            obj = IndexContainer(self.cls)
            obj.deserialize(value)
            value = obj
        return super(Index, self).__call__(value)
