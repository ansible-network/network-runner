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

import mock
import unittest

from network_runner import api
from network_runner.resources.inventory import Inventory


class BaseTestCase(unittest.TestCase):
    test_config_files = []
    parse_config = True

    def setUp(self):
        self.addCleanup(mock.patch.stopall)
        super(BaseTestCase, self).setUp()


class NetworkRunnerTestCase(BaseTestCase):
    def setUp(self):
        super(NetworkRunnerTestCase, self).setUp()

        self.testhost = 'testhost'
        self.testport = 'port123'
        self.testvlan = 37
        self.testvlans = [73, 7, 3]

        inventory = Inventory()
        self.net_runr = api.NetworkRunner(inventory=inventory)
