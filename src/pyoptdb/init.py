import logging
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)

from pyoptdb import PYOPTDB_DIR
from pyoptdb.config import _get_config


def _init():
    config = _get_config()

    dbfile = Path(config["sqlite3"].get("file", None))
    if dbfile is None:
        raise ValueError("No legal file name for sqlite3.file")

    file_archive = Path(config["archive"].get("directory", None))
    if file_archive is None:
        raise ValueError("No legal name for file_archive.directory")

    sql_script = PYOPTDB_DIR / config["sqlite3"].get("schema", None)
    if sql_script is None:
        raise ValueError("No legal file name for sqlite3['schema']")

    if dbfile.exists():
        raise FileExistsError(
            f"{dbfile} already exists, make sure to provide another file name, change directory or remove the existing database."
        )
    if not dbfile.parent.exists():
        logger.debug(f"creating directory {dbfile.parent}")
        dbfile.parent.mkdir(parents=True, exist_ok=False)

    if file_archive.exists():
        raise FileExistsError(f"{file_archive} already exists")
    if not dbfile.exists():
        logger.debug(f"creating directory {file_archive}")
        file_archive.mkdir(parents=True, exist_ok=False)

    logger.debug(f"Creating new data base file {dbfile}...")
    with sqlite3.connect(dbfile) as con:
        cur = con.cursor()
        with open(sql_script, "r") as f:
            sql = f.read()
            logger.debug(f"Executing {sql_script}...")
            cur.executescript(sql)
