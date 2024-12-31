"""Copyright 2024 Technical University Darmstadt

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from enum import Enum
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG, filename="pyoptdb.log")

__app_name__ = "pyoptdb"
__version__ = "0.1.0"

PYOPTDB_DIR = Path(__file__).parent.resolve()
CONFIG_PATH_GLOBAL = Path.home() / ".pyoptdb"
CONFIG_PATH_LOCAL = Path(".pyoptdb")
CONFIG_FILE = "pyoptdb.ini"

# if not CONFIG_PATH_LOCAL.exists():
#     FILE_ARCHIVE = CONFIG_PATH_GLOBAL / ".files"
# else:
#     FILE_ARCHIVE = CONFIG_PATH_LOCAL / ".files"


class Command(Enum):
    config = 1
    init = 2
    insert = 3
