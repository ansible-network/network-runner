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
PYTHON_RESERVED = frozenset([
    'and', 'assert', 'in', 'del', 'else', 'raise', 'from', 'if', 'continue',
    'not', 'pass', 'finally', 'while', 'yield', 'is', 'as', 'break', 'return',
    'elif', 'except', 'def', 'global', 'import', 'for', 'or', 'print',
    'lambda', 'with', 'class', 'try', 'exec'
])


def isvalidattrname(v):
    if v in PYTHON_RESERVED:
        raise ValueError("value is a reserved word")
    if not v[0].isalpha():
        raise ValueError("name must start with an alpha character")
    return True
