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

from argparse import Namespace
import os
import configparser
import logging

from pyoptdb import CONFIG_FILE, CONFIG_PATH_GLOBAL, CONFIG_PATH_LOCAL, PYOPTDB_DIR

logger = logging.getLogger(__name__)

# if not CONFIG_PATH_LOCAL.exists():
#     CONFIG_PATH = CONFIG_PATH_GLOBAL
# else:
#     CONFIG_PATH = CONFIG_PATH_LOCAL


def _get_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()

    if os.path.exists((CONFIG_PATH_LOCAL / CONFIG_FILE)):
        logger.debug(f"reading {(CONFIG_PATH_LOCAL / CONFIG_FILE)}")
        config.read((CONFIG_PATH_LOCAL / CONFIG_FILE))
    else:
        logger.debug(
            f"no local config file found, trying to read {CONFIG_PATH_GLOBAL / CONFIG_FILE}"
        )

        if not (CONFIG_PATH_GLOBAL / CONFIG_FILE).exists():

            logger.debug(
                f"{CONFIG_PATH_GLOBAL / CONFIG_FILE} does not exist. Creating default."
            )

            config["sqlite3"] = {}
            config["sqlite3"]["file"] = (
                CONFIG_PATH_LOCAL / "pyoptdb.sqlite3"
            ).as_posix()
            config["sqlite3"]["schema"] = (PYOPTDB_DIR / "schema.sql").as_posix()

            config["archive"] = {}
            config["archive"]["directory"] = (CONFIG_PATH_LOCAL / ".files").as_posix()

            if not CONFIG_PATH_GLOBAL.exists():
                logger.debug(f"creating directory {CONFIG_PATH_GLOBAL}")
                CONFIG_PATH_GLOBAL.mkdir(parents=True, exist_ok=False)

            with open(CONFIG_PATH_GLOBAL / CONFIG_FILE, "w+") as f:
                logger.debug(f"writing to {CONFIG_PATH_GLOBAL / CONFIG_FILE}")
                config.write(f)

        else:
            logger.debug(f"reading {CONFIG_PATH_GLOBAL / CONFIG_FILE}")
            config.read((CONFIG_PATH_GLOBAL / CONFIG_FILE))

    return config


def _config_pprint(config):
    for sec in config.sections():
        print(sec)
        for key, value in config[sec].items():
            print(f"\t{key}: {value}")


def _config(args: Namespace):

    config = _get_config()

    if args.LIST:
        _config_pprint(config)
    else:

        section = args.INPUT[0].split(".")[0]
        if not config.has_section(section):
            raise configparser.NoSectionError(f"section {section} does not exist")

        option = args.INPUT[0].split(".")[1]
        if not config.has_option(section, option):
            raise configparser.NoOptionError(
                f"{config[section]} has no option {option}"
            )

        value = args.INPUT[1]

        config.set(section, option, value)

        if not CONFIG_PATH_LOCAL.exists():
            logger.debug(f"creating directory {CONFIG_PATH_LOCAL}")
            CONFIG_PATH_LOCAL.mkdir(parents=True, exist_ok=False)

        with open((CONFIG_PATH_LOCAL / CONFIG_FILE), "w") as f:
            logger.debug(f"writing to {(CONFIG_PATH_LOCAL / CONFIG_FILE)}")
            config.write(f)
