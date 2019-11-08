# Copyright (c) 2018 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import pytest

from network_runner.types.objects import Object
from network_runner.types.attrs import Attribute
from network_runner.types.containers import Index, Map


class ListItem(Object):
    name = Attribute()


class DictItem(Object):
    name = Attribute()
    value = Attribute()


def test_index():
    o = Index(cls=ListItem)

    assert repr(o) == str(o.serialize())
    assert o.serialize() == []

    item = o.new()
    assert o[0] == item

    item = ListItem(name='test')
    o[0] = item
    assert o[0] == item

    items = [{'name': 'test1'}, {'name': 'test2'}, {'name': 'test3'}]
    o = Index(cls=ListItem)
    o.deserialize(items)
    assert o.serialize() == items

    o.insert(0, ListItem(name='test'))

    with pytest.raises(TypeError):
        o.insert(0, 'foo')

    with pytest.raises(TypeError):
        o[0] = 'test'

    with pytest.raises(TypeError):
        o.add("foo")

    # make sure deleting an index doesn't raise an error
    del o[0]


def test_index_comparisons():
    a = Index(cls=ListItem)
    b = Index(cls=ListItem)

    assert a.__eq__(b)
    assert a.__cmp__(b)

    b.new(name='test')

    assert a.__neq__(b)


def test_map():
    o = Map(cls=DictItem, key='name')

    assert repr(o) == str(o.serialize())
    assert o.serialize() == {}

    item = DictItem(name='foo', value='bar')
    o.new(name='foo', value='bar')
    assert o['foo'] == item

    del o['foo']

    o.add(item)
    assert o['foo'] == item

    o = Map(cls=DictItem, key='name')
    o.deserialize({'foo': {'value': 'bar'}})
    assert o['foo'] == item

    with pytest.raises(TypeError):
        o['test'] = 'test'

    keys = [key for key in o]
    assert keys == ['foo']

    assert len(o) == 1

    with pytest.raises(ValueError):
        o.new(name='foo')

    with pytest.raises(ValueError):
        o.new(value='foo')


def test_map_comparisons():
    a = Map(cls=DictItem, key='name')
    b = Map(cls=DictItem, key='name')

    assert a.__eq__(b)
    assert a.__cmp__(b)

    b.new(name='test')

    assert a.__neq__(b)
