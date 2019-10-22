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

from network_runner.types import attrs
from network_runner.types.objects import Object
from network_runner.types.attrs import Attribute
from network_runner.types.attrs import Container
from network_runner.types.containers import Map
from network_runner.types.containers import Index
from network_runner.types.validators import ChoiceValidator


class Item(Object):
    name = Attribute()


def test_create_attribute_defaults():
    a = Attribute()
    assert a.required is None
    assert a.attrtype == 'str'
    assert a.default is None
    assert a.validator is None
    assert isinstance(a._attr_type, type(str))


def test_str_attribute():
    a = Attribute(type='str')
    assert a.attrtype == 'str'
    assert isinstance(a._attr_type, type(str))


def test_bool_attribute():
    a = Attribute(type='bool')
    assert a.attrtype == 'bool'
    assert isinstance(a._attr_type, type(bool))


def test_int_attribute():
    a = Attribute(type='int')
    assert a.attrtype == 'int'
    assert isinstance(a._attr_type, type(int))


def test_list_attribute():
    a = Attribute(type='list')
    assert a.attrtype == 'list'
    assert isinstance(a._attr_type, type(list))


def test_dict_attribute():
    a = Attribute(type='dict')
    assert a.attrtype == 'dict'
    assert isinstance(a._attr_type, type(dict))


def test_invalid_attribute():
    with pytest.raises(ValueError):
        Attribute(type='foo')


def test_invalid_default_type():
    with pytest.raises(AttributeError):
        Attribute(type='str', default=1)


def test_call_list_with_default_value():
    """Ensure a copy of the default value is returned
    """
    default_value = [1, 2, 3]
    a = Attribute(type='list', default=default_value)
    z = a()
    assert id(z) != id(default_value)


def test_call_dict_with_default_value():
    """Ensure a copy of the default value is returned
    """
    default_value = {'one': 1, 'two': 2, 'three': 3}
    a = Attribute(type='dict', default=default_value)
    z = a()
    assert id(z) != id(default_value)


def test_map_container():
    c = Container('map', Item, 'name')
    r = c()
    assert isinstance(r, Map)


def test_index_container():
    c = Container('index', Item)
    r = c()
    assert isinstance(r, Index)


def test_enums():
    assert attrs.SERIALIZE_WHEN_ALWAYS == 0
    assert attrs.SERIALIZE_WHEN_PRESENT == 1
    assert attrs.SERIALIZE_WHEN_NEVER == 2


def test_attr_map():
    assert attrs._ATTR_NAME_TO_TYPE['int'] is int
    assert attrs._ATTR_NAME_TO_TYPE['bool'] is bool
    assert attrs._ATTR_NAME_TO_TYPE['list'] is list
    assert attrs._ATTR_NAME_TO_TYPE['dict'] is dict
    assert attrs._ATTR_NAME_TO_TYPE['map'] is Map
    assert attrs._ATTR_NAME_TO_TYPE['index'] is Index
    assert attrs._ATTR_NAME_TO_TYPE['str'] is str
    assert attrs._ATTR_NAME_TO_TYPE[None] is str
    assert len(attrs._ATTR_NAME_TO_TYPE) == 8


def test_bad_validator():
    with pytest.raises(AttributeError):
        Attribute(type='int', validator=ChoiceValidator([1, 2, 3]))


def test_bad_serialize_when_value():
    with pytest.raises(ValueError):
        Attribute(serialize_when=3)


def test_bad_value_type():
    with pytest.raises(TypeError):
        item = Item()
        item.name = 1


def test_map_container_missing_item_key():
    with pytest.raises(ValueError):
        Container(type='map', cls=None)


def test_invalid_container_type():
    with pytest.raises(AssertionError):
        Container(type='invalid', cls=None)
