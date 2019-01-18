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


class BaseValidator(object):

    __required_types__ = ()


class ChoiceValidator(BaseValidator):

    __required_types__ = ('str',)

    def __init__(self, choices):
        self.choices = frozenset(choices)

    def __call__(self, value):
        if value not in self.choices:
            raise AttributeError('invalid choice')


class RangeValidator(object):

    __required_types__ = ('int',)

    def __init__(self, minval, maxval):
        self.minval = minval
        self.maxval = maxval

    def __call__(self, value):
        assert isinstance(value, int), 'value must be of type <int>'
        if self.minval > value > self.maxval:
            raise AttributeError('invalid range')


class PortValidator(RangeValidator):

    def __init__(self):
        super(PortValidator, self).__init__(1, 65535)
