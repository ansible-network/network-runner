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

from six import with_metaclass, iteritems, itervalues

from network_runner.resources.attributes import Attribute


class EntityMeta(type):

    def __new__(cls, name, parents, dct):

        dct['_attributes'] = {}

        def _create_attrs(attr_dct):
            keys = list(attr_dct.keys())

            for attr_name in keys:
                value = attr_dct[attr_name]

                if isinstance(value, Attribute):
                    if attr_name.startswith('_'):
                        attr_name = attr_name[1:]
                        value.name = attr_name
                    dct['_attributes'][attr_name] = value

        # process parents first to allow more specific overrides
        for parent in parents:
            _create_attrs(parent.__dict__)

        _create_attrs(dct)

        return super(EntityMeta, cls).__new__(cls, name, parents, dct)


class Entity(with_metaclass(EntityMeta)):

    def __init__(self, **kwargs):
        required_attrs = list()

        for key, value in iteritems(self._attributes):
            try:
                attr_value = kwargs[key]
            except KeyError:
                if not value.default:
                    if value.attrtype == 'dict':
                        attr_value = {}
                    elif value.attrtype == 'list':
                        attr_value = []
                    else:
                        attr_value = None
                else:
                    attr_value = value.default

            if value.cls and not isinstance(attr_value, type(value.cls)):
                if not isinstance(attr_value, (list, dict)):
                    attr_value = attr_value or {}
                    attr_value = value.cls(**attr_value)

            setattr(self, key, attr_value)

            if value.required is True:
                required_attrs.append(key)

        for key in required_attrs:
            if getattr(self, key) is None:
                raise ValueError('missing required attribute: {}'.format(key))

        super(Entity, self).__init__()

    def __repr__(self):
        return str(self.serialize())

    def __setattr__(self, key, value):
        if key in self._attributes:
            value = self._attributes[key](value)
        elif not key.startswith('_'):
            raise AttributeError("'{}' object has no attribute '{}'".format(
                self.__class__.__name__, key))
        self.__dict__[key] = value

    def __delattr__(self, key):
        attr = self._attributes.get(key)
        if attr.required is True:
            raise ValueError('required attributes cannot be deleted')
        elif attr.cls:
            self.__dict__[key] = attr.cls()
        else:
            self.__dict__[key] = attr.default

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

    def serialize(self):
        """Serialize the provider implementation into a JSON data structure
        """
        obj = {}

        for key, attr in iteritems(self._attributes):
            value = getattr(self, key)
            if hasattr(value, 'serialize'):
                obj[key] = value.serialize()
            else:
                if attr.serialize == 'always' or attr.serialize == 'present' \
                        and value is not None:
                    obj[key] = value

        return obj

    def deserialize(self, ds):
        assert isinstance(ds, dict)
        for key, value in iteritems(ds):
            attr = getattr(self, key)
            if hasattr(attr, 'deserialize'):
                attr.deserialize(value)
            else:
                setattr(self, key, value)


class Collection(MutableSequence):

    def __init__(self, *args, **kwargs):
        super(Collection, self).__init__(*args, **kwargs)
        self.items = list()

    def __repr__(self):
        return str(self.serialize())

    def __getitem__(self, index):
        return self.__dict__['items'][index]

    def __setitem__(self, index, value):
        if not isinstance(value, self.__item_class__):
            raise TypeError('invalid type')
        self.__dict__['items'][index] = value

    def __delitem__(self, index):
        del self.__dict__['items'][index]

    def __len__(self):
        return len(self.__dict__['items'])

    def insert(self, index, obj):
        self.items.insert(index, obj)

    def add(self, obj):
        if not isinstance(obj, self.__item_class__):
            raise TypeError('invalid object type')
        self.append(obj)

    def new(self, **kwargs):
        obj = self.__item_class__(**kwargs)
        self.add(obj)
        return obj

    def get(self, index):
        return self[index]

    def get_all(self):
        return [i.serialize() for i in self.items]

    def remove(self, index):
        del self[index]

    def deserialize(self, ds):
        assert isinstance(ds, list)
        for item in ds:
            obj = self.__item_class__()
            obj.deserialize(item)
            self.add(obj)

    def serialize(self):
        obj = {}
        if hasattr(self, '__item_id__'):
            for key, value in iteritems(self.items):
                obj[key] = value.serialize()
        elif hasattr(self, '__item_class__'):
            obj = [o.serialize() for o in self.items]
        else:
            obj = [o.serialize() for o in itervalues(self.items)]
        return obj


class KeyedCollection(MutableMapping):

    __recursive__ = False

    def __init__(self, *args, **kwargs):
        super(KeyedCollection, self).__init__(*args, **kwargs)
        self.objects = {}

    def __repr__(self):
        return str(self.serialize())

    def __getitem__(self, key):
        return self.__dict__['objects'][key]

    def __setitem__(self, key, value):
        if not isinstance(value, self.__item_class__):
            raise TypeError('invalid type')
        self.__dict__['objects'][key] = value

    def __delitem__(self, key):
        del self.__dict__['objects'][key]

    def __iter__(self):
        return iter(self.__dict__['objects'])

    def __len__(self):
        return len(self.__dict__['objects'])

    def add(self, obj):
        assert isinstance(obj, self.__item_class__)

        if self.__recursive__ is True:
            name = self.__class__.__name__.lower()
            obj._attributes[name] = Attribute(cls=self.__class__)
            setattr(obj, name, self.__class__())

        key = getattr(obj, self.__item_key__)
        self[key] = obj

    def new(self, **kwargs):
        try:
            if kwargs[self.__item_key__] in self:
                raise ValueError('entry already exists')
        except KeyError:
            raise ValueError('missing required argument: {}'.format(
                self.__item_key__))
        obj = self.__item_class__(**kwargs)
        self.add(obj)
        return obj

    def remove(self, key):
        del self[key]

    def deserialize(self, ds):
        assert isinstance(ds, dict)
        for key, value in iteritems(ds):
            value[self.__item_key__] = key
            obj = self.__item_class__(**value)
            obj.deserialize(value)
            self[key] = obj

    def serialize(self):
        obj = {}
        for key, value in iteritems(self.objects):
            obj[key] = value.serialize()
        return obj
