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


def test_map():
    o = Map(cls=DictItem, key='name')

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
