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

from collections import MutableMapping, MutableSequence

from six import iteritems


class Container(object):

    def __init__(self, cls):
        self.cls = cls
        self.store = None

    def __repr__(self):
        return json.dumps(self.serialize())

    def __eq__(self, other):
        return self.serialize() == other.serialize()

    def __neq__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        return self.__eq__(other)

    def __deepcopy__(self, memo):
        kwargs = self.serialize()
        o = type(self)(self.cls)
        o.deserialize(kwargs)
        return o

    def new(self, **kwargs):
        raise NotImplementedError

    def serialzie(self):
        raise NotImplementedError

    def deserialize(self, ds):
        raise NotImplementedError


class IndexContainer(MutableSequence, Container):

    def __init__(self, cls):
        super(IndexContainer, self).__init__(cls)
        self.store = list()

    def __getitem__(self, index):
        return self.__dict__['store'][index]

    def __setitem__(self, index, value):
        if not isinstance(value, self.cls):
            raise TypeError('invalid type')
        self.__dict__['store'][index] = value

    def __delitem__(self, index):
        del self.__dict__['store'][index]

    def __len__(self):
        return len(self.__dict__['store'])

    def insert(self, index, value):
        if not isinstance(value, self.cls):
            raise TypeError('invalid type')
        self.store.insert(index, value)

    def new(self, **kwargs):
        obj = self.cls(**kwargs)
        self.append(obj)
        return obj

    def __setstate__(self, ds):
        assert isinstance(ds, list)
        for item in ds:
            self.new(**item)

    deserialize = __setstate__

    def __getstate__(self):
        return [o.serialize() for o in self.store]

    serialize = __getstate__


class MapContainer(MutableMapping, Container):

    def __init__(self, cls):
        super(MapContainer, self).__init__(cls)
        self.store = {}

    def __getitem__(self, index):
        return self.__dict__['store'][index]

    def __setitem__(self, index, value):
        if not isinstance(value, self.cls):
            raise TypeError('invalid type')
        self.__dict__['store'][index] = value

    def __delitem__(self, index):
        del self.__dict__['store'][index]

    def __len__(self):
        return len(self.__dict__['store'])

    def __iter__(self):
        return iter(self.__dict__['store'])

    def new(self, _key, **kwargs):
        try:
            if kwargs[_key] in self:
                raise ValueError("item already exists")
        except KeyError:
            obj = self.cls(**kwargs)
            self[_key] = obj
            return obj

    def __setstate__(self, ds):
        assert isinstance(ds, dict)
        for key, value in iteritems(ds):
            if not value:
                value = {}
            self.new(key, **value)

    deserialize = __setstate__

    def __getstate__(self):
        obj = {}
        for key, value in iteritems(self.store):
            if hasattr(value, 'serialize'):
                obj[key] = value.serialize()
            else:
                obj[key] = value
        return obj

    serialize = __getstate__
