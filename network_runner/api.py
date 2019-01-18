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
import ansible_runner

from network_runner import exceptions
from network_runner.resources.ansible import Playbook
from network_runner.resources.inventory import Inventory


def run(playbook, inventory):
    assert isinstance(playbook, Playbook)
    assert isinstance(inventory, Inventory)

    # invoke ansible networking via ansible runner
    result = ansible_runner.run(playbook=playbook.serialize(),
                                inventory=inventory.serialize(),
                                settings={'pexpect_use_poll': False})

    # check for failure
    if result.status == 'failed' or \
            (result.stats and result.stats.get('failures', [])):
        raise exceptions.AnsibleRunnerException(' '.join(result.stdout))

    return result
