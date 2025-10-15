#     Copyright 2023, --- Kam, mailto:kay.hayen@gmail.com
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

import logging

from machineroom.sql import ServerRoom
from machineroom.util import *

logger1 = logging.getLogger("web3.RequestManager")
logger2 = logging.getLogger("web3.providers.HTTPProvider")
logger3 = logging.getLogger("urllib3.connectionpool")
logger4 = logging.getLogger("paramiko.transport")
logger5 = logging.getLogger("invoke")
logger2.setLevel(logging.ERROR)
logger1.setLevel(logging.ERROR)
logger3.setLevel(logging.ERROR)
logger4.setLevel(logging.ERROR)
logger5.setLevel(logging.ERROR)

__version__ = '0.47.7'