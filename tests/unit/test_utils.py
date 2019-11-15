# Copyright (c) 2019 Red Hat, Inc.
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
import json

from network_runner import utils
from network_runner.types.objects import Object
from network_runner.types.attrs import String


class StdoutTest(Object):

    name = String()


def test_print_json(capsys):
    test = StdoutTest(name='test')
    utils.print_json(test)
    out, err = capsys.readouterr()
    assert out.strip() == json.dumps(test.serialize(), indent=4).strip()
