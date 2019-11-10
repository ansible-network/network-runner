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
from network_runner.types.attrs import String, Integer, Boolean, List, Dict


class Instance(Object):
    name = String()
    strattr = String()
    intattr = Integer()
    boolattr = Boolean()
    listattr = List()
    dictattr = Dict()


class InstanceWithDefaults(Object):
    name = String()
    strattr = String(default='string')
    intattr = Integer(default=0)
    boolattr = Boolean(default=False)
    listattr = List(default=[1, 2, 3])
    dictattr = Dict(default={'one': 1, 'two': 2, 'three': 3})


class InstanceWithRequiredAttr(Object):
    required = String(required=True)


def test_instance():
    o = Instance()
    assert repr(o) is not None

    z = Instance()
    assert o.__eq__(z)
    assert o.__cmp__(z)

    z.name = 'test'
    assert o.__neq__(z)


def test_set_strattr():
    o = Instance()
    o.strattr = 'test'
    with pytest.raises(TypeError):
        o.strattr = 1
        o.strattr = True
        o.strattr = [1, 2, 3]
        o.strattr = {'one': 1, 'two': 2, 'three': 3}


def test_set_intattr():
    o = Instance()
    o.intattr = 1
    with pytest.raises(TypeError):
        o.intattr = "string"
        o.intattr = True
        o.intattr = [1, 2, 3]
        o.intattr = {'one': 1, 'two': 2, 'three': 3}


def test_set_boolattr():
    o = Instance()
    o.boolattr = True
    o.boolattr = False
    with pytest.raises(TypeError):
        o.boolattr = "string"
        o.boolattr = 0
        o.boolattr = 1
        o.boolattr = [1, 2, 3]
        o.boolattr = {'one': 1, 'two': 2, 'three': 3}


def test_set_listattr():
    o = Instance()
    o.listattr = [1, 2, 3]
    with pytest.raises(TypeError):
        o.listattr = "string"
        o.listattr = 0
        o.listattr = True
        o.listattr = {'one': 1, 'two': 2, 'three': 3}


def test_set_dictattr():
    o = Instance()
    o.dictattr = {'one': 1, 'two': 2, 'three': 3}
    for value in ('string', 0, True, [1, 2, 3]):
        with pytest.raises(TypeError):
            o.dictattr = value


def test_del_strattr():
    o = Instance()
    assert o.strattr is None
    o.strattr = 'test'
    assert o.strattr == 'test'
    del o.strattr
    assert o.strattr is None


def test_del_intattr():
    o = Instance()
    assert o.intattr is None
    o.intattr = 0
    assert o.intattr == 0
    del o.intattr
    assert o.intattr is None


def test_del_boolattr():
    o = Instance()
    assert o.boolattr is None
    o.boolattr = True
    assert o.boolattr is True
    del o.boolattr
    assert o.boolattr is None


def test_del_listattr():
    o = Instance()
    assert o.listattr == []
    o.listattr = [1, 2, 3]
    assert o.listattr == [1, 2, 3]
    del o.listattr
    assert o.listattr == []


def test_del_dictattr():
    o = Instance()
    assert o.dictattr == {}
    o.dictattr = {'one': 1, 'two': 2, 'three': 3}
    assert o.dictattr == {'one': 1, 'two': 2, 'three': 3}
    del o.dictattr
    assert o.dictattr == {}


def test_strattr_with_defaults():
    o = InstanceWithDefaults()
    assert o.strattr == 'string'
    o.strattr = 'text'
    assert o.strattr == 'text'
    del o.strattr
    assert o.strattr == 'string'


def test_intattr_with_defaults():
    o = InstanceWithDefaults()
    assert o.intattr == 0
    o.intattr = 2
    assert o.intattr == 2
    del o.intattr
    assert o.intattr == 0


def test_boolattr_with_defaults():
    o = InstanceWithDefaults()
    assert o.boolattr is False
    o.boolattr = True
    assert o.boolattr is True
    del o.boolattr
    assert o.boolattr is False


def test_listattr_with_defaults():
    o = InstanceWithDefaults()
    assert o.listattr == [1, 2, 3]
    o.listattr = [4, 5, 6]
    assert o.listattr == [4, 5, 6]
    del o.listattr
    assert o.listattr == [1, 2, 3]


def test_dictattr_with_defaults():
    o = InstanceWithDefaults()
    assert o.dictattr == {'one': 1, 'two': 2, 'three': 3}
    o.dictattr = {'four': 4, 'five': 5, 'six': 6}
    assert o.dictattr == {'four': 4, 'five': 5, 'six': 6}
    del o.dictattr
    assert o.dictattr == {'one': 1, 'two': 2, 'three': 3}


def test_object_init_with_values():
    o = Instance(strattr='string', intattr=100, boolattr=True,
                 listattr=[1, 2, 3], dictattr={'one': 1, 'two': 2, 'three': 3})
    assert o.strattr == 'string'
    assert o.intattr == 100
    assert o.boolattr is True
    assert o.listattr == [1, 2, 3]
    assert o.dictattr == {'one': 1, 'two': 2, 'three': 3}


def test_object_with_required_attr():
    o = InstanceWithRequiredAttr(required='foo')
    assert o.required == 'foo'

    with pytest.raises(ValueError):
        del o.required

    with pytest.raises(ValueError):
        InstanceWithRequiredAttr()


class Aliases(Object):

    attr1 = String(
        aliases=('attr2', 'attr3')
    )

    attr2 = String()


def test_attr1_alias():
    o = Aliases()

    o.attr1 = 'test'

    assert o.attr1 == 'test'
    assert o.attr2 is None
    assert o.attr3 == 'test'

    o.attr2 = 'test2'

    assert o.attr1 == 'test'
    assert o.attr2 == 'test2'
    assert o.attr3 == 'test'

    del o.attr1

    assert o.attr1 is None
    assert o.attr2 == 'test2'
    assert o.attr3 is None

    o.attr1 = 'test'
    del o.attr2

    assert o.attr1 == 'test'
    assert o.attr2 is None
    assert o.attr3 == 'test'
