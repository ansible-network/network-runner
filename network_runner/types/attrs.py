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
from unicodedata import normalize

from six import PY2

from network_runner.types.containers import Map
from network_runner.types.containers import Index


SERIALIZE_WHEN_ALWAYS = 0
SERIALIZE_WHEN_PRESENT = 1
SERIALIZE_WHEN_NEVER = 2


_ATTR_NAME_TO_TYPE = {
    'int': int,
    'bool': bool,
    'list': list,
    'dict': dict,
    'map': Map,
    'index': Index,
    'str': str,
    None: str
}


class Attribute(object):

    def __init__(self, default=None, type='str', required=None,
                 validator=None, serialize_when=None, aliases=None):

        self.required = required
        self.attrtype = type
        self.default = None
        self.validator = validator
        self.aliases = aliases or []
        self.name = None
        self.serialize_when = serialize_when or SERIALIZE_WHEN_ALWAYS

        if validator and self.attrtype not in validator.__required_types__:
            raise AttributeError('invalid validator for attr type')

        if self.attrtype not in _ATTR_NAME_TO_TYPE:
            raise ValueError("invalid attrtype specified")

        self._attr_type = _ATTR_NAME_TO_TYPE[self.attrtype]

        if serialize_when is not None:
            if serialize_when not in (0, 1, 2):
                raise ValueError("invalid value for serialize_when")

        if default is None and self.attrtype in ('list', 'dict'):
            if self.attrtype == 'list':
                default = []
            elif self.attrtype == 'dict':
                default = {}

        if default is not None:
            if not isinstance(default, self._attr_type):
                raise AttributeError(
                    "attribute default must of of type '{}'".format(type)
                )
            self.default = default

    def __call__(self, value=None):
        if value is not None:
            if self.attrtype == 'bool' and not isinstance(value, bool):
                raise TypeError('expected type bool')

            if PY2 and isinstance(value, unicode):
                value = normalize('NFKD', value).encode('ascii', 'ignore')

            if not isinstance(value, self._attr_type):
                raise TypeError(
                    "attribute must be of type '{}', "
                    "got '{}'".format(self.attrtype, type(value))
                )

            value = self._attr_type(value)

            if self.validator:
                self.validator(value)

        elif self.default is not None:
            if hasattr(self.default, 'copy'):
                value = self.default.copy()
            elif isinstance(self.default, list):
                value = list(self.default)
            else:
                value = self.default

        if self.required is True and value is None:
            raise ValueError("missing required attribute")

        return value


class Container(Attribute):

    def __init__(self, type, cls, item_key=None):
        self.item_key = item_key
        self.cls = cls

        assert type in ('map', 'index'), "invalid container type"

        if type == 'map' and item_key is None:
            raise ValueError("missing required args 'key' for type 'map'")

        super(Container, self).__init__(type=type)

    def __call__(self, value=None):
        if self.attrtype == 'map':
            obj = Map(self.cls, self.item_key)

        elif self.attrtype == 'index':
            obj = Index(self.cls)

        if value:
            obj.deserialize(value)

        return obj
