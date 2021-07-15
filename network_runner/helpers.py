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
from network_runner import exceptions

PYTHON_RESERVED = frozenset([
    'and', 'assert', 'in', 'del', 'else', 'raise', 'from', 'if', 'continue',
    'not', 'pass', 'finally', 'while', 'yield', 'is', 'as', 'break', 'return',
    'elif', 'except', 'def', 'global', 'import', 'for', 'or', 'print',
    'lambda', 'with', 'class', 'try', 'exec'
])


class FakeTextIO(object):
    def __init__(self):
        self._buff = ""

    def write(self, out_stream):
        self._buff += out_stream

    def buff(self):
        return self._buff

    def flush(self):
        return


def isvalidattrname(v):
    if v in PYTHON_RESERVED:
        raise ValueError("value is a reserved word")
    if not v[0].isalpha():
        raise ValueError("name must start with an alpha character")
    return True


def format_port_config(data, os):
    """Use standard format json string replace port configuration string

    :param data: The output of ansible play command
    :type data: String
    :param os: The system of the switch
    :type os: String

    :returns: String
    """
    # find source port configuration json string
    source_config_json = ''
    count = 0
    for char in data:
        if char == '{':
            count += 1
            # begin of json string
            if count == 1:
                source_config_json = ''
        elif char == '}':
            count -= 1
            # end of json string
            if count == 0:
                source_config_json = source_config_json + '}'
        if count > 0:
            source_config_json += char
    if count != 0:
        raise exceptions.NetworkRunnerException(
            'invaild json format: '.join(source_config_json))
    # transform source port configuration to target port configuration
    source_config = json.loads(source_config_json.replace('\n', ' '))
    target_config = {
        'mode': None,
        'vlan': None,
        # format 1-12,15,17-20
        'trunked_vlans': '',
    }
    if os == "fos":
        lines = source_config['stdout_lines'][0]
        for line in lines:
            # deal switchport mode
            if line.startswith('switchport mode '):
                target_config['mode'] = line.replace(
                    'switchport mode ', '')
            # deal vlan
            if line.startswith('switchport access vlan '):
                target_config['vlan'] = int(line.replace(
                    'switchport access vlan ', ''))
            # deal trunked vlans
            if line.startswith('switchport trunk allowed vlan '):
                target_config['trunked_vlans'] = line.replace(
                    'switchport trunk allowed vlan ', '')
    else:
        raise exceptions.NetworkRunnerException('invaild os type')
    # replace source port configuration json to target port configuration json
    return data.replace(source_config_json, json.dumps(target_config))
