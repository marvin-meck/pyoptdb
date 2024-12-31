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

# import logging

from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from pyoptdb import Command
from pyoptdb.insert import _insert
from pyoptdb.config import _config
from pyoptdb.init import _init

# logging.basicConfig(level=logging.DEBUG)
# filename='pyoptdb.log', encoding='utf-8',

parser = ArgumentParser("pyoptdb")

subparsers = parser.add_subparsers(dest="COMMAND", required=True)

parser_insert = subparsers.add_parser("insert", help="generate insert query")
parser_config = subparsers.add_parser("config", help="configure pyoptdb")
parser_init = subparsers.add_parser("init", help="initialize a pyoptdb database")

parser_insert.add_argument("-m", "--model-file", dest="MODEL", required=True)
parser_insert.add_argument("SOL")

parser_insert.add_argument(
    "-d", "--dat-file", dest="DATA", required=False, default=None
)

parser_config.add_argument("INPUT", nargs="*", default=[])
parser_config.add_argument(
    "-l",
    "--list",
    dest="LIST",
    default=False,
    type=bool,
    action=BooleanOptionalAction,
    help="provide a listing of the current config",
)


def _parse_args() -> Namespace:
    args = parser.parse_args()

    if Command[args.COMMAND] == Command.config:
        if not args.LIST and len(args.INPUT) != 2:
            parser.error("Expected exactly two positional arguments")

    return args


def main():
    args = _parse_args()

    cmd = Command[args.COMMAND]

    if cmd == Command.config:
        _config(args)
    elif cmd == Command.insert:
        _insert(args)
    elif cmd == Command.init:
        _init()
