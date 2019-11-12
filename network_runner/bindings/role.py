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
import os

from functools import partial
from collections import namedtuple

from six import iteritems

from yaml import safe_load

from network_runner.types.objects import Object
from network_runner.types import attrs
from network_runner.types import validators
from network_runner.helpers import PYTHON_RESERVED
from network_runner.helpers import get_role_path
from network_runner.helpers import to_text
from network_runner.helpers import to_list
from network_runner.models.modules import ImportRole
from network_runner.exceptions import NetworkRunnerException


VALIDATOR_TYPE_MAP = {
    'range': validators.RangeValidator,
    'choice': validators.ChoiceValidator,
    'port': validators.PortValidator
}


ATTR_TYPE_MAP = {
    'str': attrs.String,
    'int': attrs.Integer,
    'bool': attrs.Boolean,
    'list': attrs.List,
    'dict': attrs.Dict,
    'map': attrs.Map,
    'index': attrs.Index,
    'dject': attrs.Object,
    None: attrs.String
}


def _invoke_action(_action, **kwargs):

    if set(kwargs).difference(_action.args):
        raise AttributeError("unknown kwargs")

    for key, value in iteritems(_action.args):
        if value.get('required') is True and key not in kwargs:
            if value.get('default') is not None:
                raise ValueError("missing required value")

        if value.get('default') is not None and key not in kwargs:
            kwargs[key] = value['default']

        passedval = kwargs.get(key)
        validators = to_list(value.get('validators', []))

        if passedval:
            # perform type checks
            vartype = value.get('type', 'str')

            if vartype == 'int':
                passedval = int(passedval)
            elif vartype == 'bool':
                passedval = bool(passedval)
            elif vartype == 'list':
                passedval = list(passedval)
            elif vartype == 'dict':
                if not isinstance(passedval, dict):
                    raise ValueError("var type must be of type dict")
            elif vartype in _action.models:
                if not isinstance(passedval, _action.models[vartype]):
                    raise ValueError(
                        "var type must be of type {}".format(vartype)
                    )
                passedval = passedval.serialize()
            else:
                passedval = str(passedval)

            for item in validators:
                func = _action.validators[item]
                func(passedval)

            kwargs[key] = passedval

    import_role = ImportRole(name=_action.name)

    tasks_from = _action.tasks_from
    if tasks_from:
        import_role.tasks_from = tasks_from

    task = import_role.to_task()
    task.vars = kwargs
    task.vars.update(_action.vars or {})

    return task


def _create_object(_models, _name, **kwargs):
    if _name not in _models:
        raise NetworkRunnerException("requested model does not exist")
    return _models[_name](**kwargs)


def get_role_bindings(path):
    """Returns the role bindings

    This function will return the role bindings dictionary if it
    exists in the role specified by `path` otherwise this
    function will generate an exception.

    :param path: the full path to the role
    :type path: str

    :returns: the runner spec as a dictionary
    :rtype: dict

    :raises: NetworkRunnerException
    """
    for ext in ('yaml', 'yml'):
        fullpath = os.path.join(to_text(path), 'bindings.{}'.format(ext))
        if os.path.exists(fullpath):
            return safe_load(open(fullpath))
    raise NetworkRunnerException("role bindings not found")


def load(role_name):
    """Load the role bindings return a programmable instance

    Load and parse the role bindings YAML file and dynamically create
    a new instance with methods and models that are mapped from
    the bindings file.

    :param role_name: the name of the role to generate bindings for
    :type role_name: str

    :returns: a role programmable instance
    :rtype: object
    """
    role_path = get_role_path(role_name)

    for c in ('-', '.'):
        role_name = role_name.replace(c, '_')

    bindings = get_role_bindings(role_path)
    actions = bindings.get('actions', {})
    validators = {}

    for name, kwargs in iteritems(bindings.get('validators', {})):
        validator_type = kwargs.pop('type')
        cls = VALIDATOR_TYPE_MAP[validator_type]
        validators[name] = cls(**kwargs)

    if list(filter(lambda x: x in PYTHON_RESERVED, actions)):
        raise ValueError("name is using a reserved keyword")

    models = {}

    for name, kwargs in iteritems(bindings.get('models', {})):
        name = to_text(name)
        attrs = dict()

        for key, value in iteritems(kwargs):
            attr_type = value.pop('type', None)

            if 'name' not in value:
                value['name'] = key

            requested_validators = value.pop('validators', [])
            value['validators'] = list()

            for item in to_list(requested_validators):
                value['validators'].append(validators[item])

            attrs[key] = ATTR_TYPE_MAP[attr_type](**value)

        models[name] = type(name, (Object,), attrs)

    action = namedtuple(
        'action', ('name', 'args', 'vars', 'models',
                   'validators', 'tasks_from')
    )

    dct = {'new': partial(_create_object, models)}

    for name, kwargs in iteritems(actions):
        name = to_text(name)
        kwargs['name'] = name
        kwargs['models'] = models
        kwargs['validators'] = validators

        for item in set(action._fields).difference(kwargs):
            kwargs[item] = None

        dct[name] = partial(_invoke_action, action(**kwargs))

    cls = type(role_name, (object,), dct)

    return cls()
