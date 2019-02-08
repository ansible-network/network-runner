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
from six import PY2


class Attribute(object):

    def __init__(self, default=None, type='str', required=None, cls=None,
                 serialize='always', validator=None, recursive=None):

        self.required = required
        self.attrtype = type
        self.cls = cls
        self.default = default
        self.name = None
        self.validator = validator
        self.recursive = recursive

        self.serialize = serialize or 'always'
        assert self.serialize in ('always', 'never', 'present')

        if validator and self.attrtype not in validator.__required_types__:
            raise AttributeError('invalid validator for attr type')

        if self.attrtype == 'int':
            self._attr_type = int
        elif self.attrtype == 'bool':
            self._attr_type = bool
        elif self.attrtype == 'list':
            self._attr_type = list
        elif self.attrtype == 'dict':
            self._attr_type = dict
        else:
            self._attr_type = str

    def __call__(self, value):
        if value is not None:
            if self.attrtype not in ('list', 'dict') and self.cls is None:

                if self.attrtype == 'bool' and not isinstance(value, bool):
                    raise ValueError('expected type bool')

                value = self._attr_type(value)

                if not isinstance(value, self._attr_type):
                    raise ValueError('invalid attribute type: %s' % value)

            if PY2 and isinstance(value, unicode):
                value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')

            if self.validator:
                self.validator(value)

        return value
