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


class Index(MutableSequence):

    def __init__(self, cls):
        self.items = list()
        self.cls = cls

    def __repr__(self):
        return json.dumps(self.serialize())

    def __eq__(self, other):
        return self.serialize() == other.serialize()

    def __neq__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        return self.__eq__(other)

    def __getitem__(self, index):
        return self.__dict__['items'][index]

    def __setitem__(self, index, value):
        if not isinstance(value, self.cls):
            raise TypeError('invalid type')
        self.__dict__['items'][index] = value

    def __delitem__(self, index):
        del self.__dict__['items'][index]

    def __len__(self):
        return len(self.__dict__['items'])

    def __deepcopy__(self, memo):
        kwargs = self.serialize()
        o = type(self)(self.cls)
        o.deserialize(kwargs)
        return o

    def insert(self, index, value):
        if not isinstance(value, self.cls):
            raise TypeError('invalid type')
        self.items.insert(index, value)

    def add(self, obj):
        if not isinstance(obj, self.cls):
            raise TypeError('invalid object type')
        self.append(obj)

    def new(self, **kwargs):
        obj = self.cls(**kwargs)
        self.add(obj)
        return obj

    def __setstate__(self, ds):
        assert isinstance(ds, list)
        for item in ds:
            self.new(**item)

    deserialize = __setstate__

    def __getstate__(self):
        return [o.serialize() for o in self.items]

    serialize = __getstate__


class Map(MutableMapping):

    def __init__(self, cls, key):
        self.objects = {}
        self.cls = cls
        self.key = key

    def __repr__(self):
        return json.dumps(self.serialize())

    def __eq__(self, other):
        return self.serialize() == other.serialize()

    def __neq__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        return self.__eq__(other)

    def __getitem__(self, key):
        return self.__dict__['objects'][key]

    def __setitem__(self, key, value):
        if not isinstance(value, self.cls):
            raise TypeError("invalid type")
        self.__dict__['objects'][key] = value

    def __delitem__(self, key):
        del self.__dict__['objects'][key]

    def __iter__(self):
        return iter(self.__dict__['objects'])

    def __len__(self):
        return len(self.__dict__['objects'])

    def __deepcopy__(self, memo):
        kwargs = self.serialize()
        o = type(self)(self.cls, self.key)
        o.deserialize(kwargs)
        return o

    def add(self, obj):
        assert isinstance(obj, self.cls)
        key = getattr(obj, self.key)
        if key not in self:
            self[key] = obj

    def new(self, **kwargs):
        try:
            if kwargs[self.key] in self:
                raise ValueError("item already exists")
        except KeyError:
            raise ValueError("missing required argument: {}".format(self.key))

        obj = self.cls(**kwargs)
        self.add(obj)

        return obj

    def __setstate__(self, ds):
        assert isinstance(ds, dict)
        for key, value in iteritems(ds):
            if not value:
                value = {}
            value[self.key] = key
            self.new(**value)

    deserialize = __setstate__

    def __getstate__(self):
        obj = {}
        for key, value in iteritems(self.objects):
            if hasattr(value, 'serialize'):
                obj[key] = value.serialize()
            else:
                obj[key] = value
        return obj

    serialize = __getstate__
