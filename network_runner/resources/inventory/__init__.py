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
from network_runner.resources import Entity
from network_runner.resources.attributes import Attribute
from network_runner.resources.inventory.children import Children
from network_runner.resources.inventory.hosts import Hosts


class Inventory(Entity):

    _hosts = Attribute(cls=Hosts)
    _vars = Attribute(type='dict')
    _children = Attribute(cls=Children)

    def serialize(self):
        obj = super(Inventory, self).serialize()
        return {'all': obj}

    def deserialize(self, obj):
        super(Inventory, self).deserialize(obj['all'])
