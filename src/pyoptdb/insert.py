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

import hashlib
import importlib
import io
import pathlib
import shutil
import sys
import sqlite3
import uuid

import pyomo.environ as pyo
from pyomo.opt import SolverResults

# from pyoptdb import CONFIG_PATH_LOCAL, CONFIG_PATH_GLOBAL
from pyoptdb.config import _get_config

# MODEL_UUID1 = uuid.uuid1()
DATA_SET_UUID1 = uuid.uuid1()
SOLUTION_UUID1 = uuid.uuid1()


def _get_model(
    model_file: pathlib.Path, datacmd_file: pathlib.Path = None
) -> pyo.ConcreteModel:
    sys.path.append(str(model_file.parent))

    module = importlib.import_module(model_file.stem)
    model = module.pyomo_create_model()

    if isinstance(model, pyo.AbstractModel):
        return model.create_instance(filename=datacmd_file.as_posix())
    else:
        return model


def str_repr_index(idx):
    # if isinstance(idx, tuple):
    str_repr = str(idx).replace(
        "'", "''"
    )  # "(" + ",".join(f"''{i}''" for i in idx) + ")"
    # else:
    #     str_repr = f"\\'{idx}\\'"
    return str_repr


def _load_solution(model: pyo.ConcreteModel, sol_file: pathlib.Path):

    results = SolverResults()
    results.read(filename=sol_file)

    # fix the solution object, otherwise results.solutions.load_from(...) won't work
    results.solution(0)._cuid = False
    results.solution.Constraint = {}

    model.solutions.load_from(results)

    # default_variable_value=0 doesn't work because smap_id = None,
    # so we set them manually
    for var in model.component_data_objects(pyo.Var):
        if var.value is None:
            var.value = 0


def _insert_into_files(
    ostream, filename: pathlib.Path, kind: str, _id: str, file_archive: str
):

    with open(filename, "r") as f:
        lines = f.read()

    checksum = hashlib.md5(lines.encode("utf-8"))
    dst = file_archive / (checksum.hexdigest() + filename.suffix)

    shutil.copyfile(filename, dst)

    ostream.write(
        "INSERT OR IGNORE INTO files(file_location,md5_checksum,file_kind,file_type) \n"
        + "VALUES(\n\t'{}',\n\t'{}',\n\t'{}',\n\t'{}'\n);\n\n".format(
            dst.as_posix(), checksum.hexdigest(), kind, "".join(filename.suffixes)
        )
    )

    if kind == "model":
        ostream.write(
            "INSERT OR IGNORE INTO model_has_file(model_id,file_id)\n"
            + "VALUES (\n\t(\n\t{}\n\t),\n\t(\n\t{}\n\t)\n);\n\n".format(
                "SELECT model_id from models " f"WHERE model_name='{_id}'",
                "SELECT file_id FROM files "
                f"WHERE md5_checksum='{checksum.hexdigest()}'",
            )
        )
    elif kind == "data":
        ostream.write(
            "INSERT OR IGNORE INTO data_set_has_file(data_set_id,file_id)\n"
            + "VALUES (\n\t(\n\t{}\n\t),\n\t(\n\t{}\n\t)\n);\n\n".format(
                "SELECT data_set_id from data_sets " f"WHERE data_set_uuid1='{_id}'",
                "SELECT file_id FROM files "
                f"WHERE md5_checksum='{checksum.hexdigest()}'",
            )
        )
    elif kind == "sol":
        ostream.write(
            "INSERT OR IGNORE INTO solution_has_file(solution_id,file_id) \n"
            + "VALUES (\n\t(\n\t{}\n\t),\n\t(\n\t{}\n\t)\n);\n\n".format(
                "SELECT solution_id from solutions " f"WHERE solution_uuid1='{_id}'",
                "SELECT file_id FROM files "
                f"WHERE md5_checksum='{checksum.hexdigest()}'",
            )
        )
    else:
        raise ValueError(f"unknown `file_type` {kind}")


def _insert_into_params(ostream, param: pyo.Param):
    ostream.write(
        "INSERT OR IGNORE INTO parameters(model_id,param_name,description) \n"
        + "VALUES (\n\t(\n\tSELECT model_id FROM models\n\t\tWHERE\n\t\tmodel_name='{}'\n\t),\n\t'{}',\n\t'{}'\n);\n\n".format(
            param.model().name, param.name, param.doc
        )
    )


def _insert_into_sets(ostream, _set: pyo.Set):
    ostream.write(
        "INSERT OR IGNORE INTO sets(model_id,set_name,description) \n"
        + "VALUES (\n\t(\n\tSELECT model_id FROM models\n\t\tWHERE\n\t\tmodel_name='{}'\n\t),\n\t'{}',\n\t'{}'\n);\n\n".format(
            _set.model().name, _set.name, _set.doc
        )
    )


def _insert_into_vars(ostream, var: pyo.Var):
    ostream.write(
        "INSERT OR IGNORE INTO variables(model_id,var_name,description) \n"
        + "VALUES (\n\t(\n\tSELECT model_id FROM models\n\t\tWHERE\n\t\tmodel_name='{}'\n\t),\n\t'{}',\n\t'{}'\n);\n\n".format(
            var.model().name, var.name, var.doc
        )
    )


def _insert_or_ignore_model(
    ostream,
    model: pyo.ConcreteModel,
    _class: str,
    is_convex: bool,
    filename: str,
    file_archive: str,
):
    ostream.write(
        "INSERT OR IGNORE INTO models(model_name,model_class,model_is_convex,description) \n"
        + "VALUES(\n\t'{}',\n\t'{}',\n\t{},\n\t'{}'\n);\n\n".format(
            model.name, _class, 1 if is_convex else 0, model.doc
        )
    )

    for name in model.component_map(pyo.Param):
        _insert_into_params(ostream, getattr(model, name))

    for name in model.component_map(pyo.Set):
        _insert_into_sets(ostream, getattr(model, name))

    for name in model.component_map(pyo.Var):
        _insert_into_vars(ostream, getattr(model, name))

    _insert_into_files(
        ostream, filename, "model", _id=model.name, file_archive=file_archive
    )


def _insert_or_ignore_data_set(
    ostream, model: pyo.ConcreteModel, filename: str, file_archive: str
):

    ostream.write(
        "INSERT OR IGNORE INTO data_sets(data_set_uuid1,model_id) \n"
        + "VALUES(\n\t'{}',\n\t(\n\t\tSELECT model_id from models\n\t\tWHERE model_name='{}'\n\t)\n);\n\n".format(
            DATA_SET_UUID1, model.name
        )
    )

    for name in model.component_map(pyo.Param):
        param = getattr(model, name)

        ostream.write(
            "INSERT OR IGNORE INTO parameter_data(data_set_id,param_id,index_str,value)\nVALUES\n"
            + ",\n".join(
                "\t("
                + "\n\t\t({}),\n\t\t({}),\n\t\t'{}',\n\t\t{}\n\t".format(
                    f"SELECT data_set_id from data_sets WHERE data_set_uuid1='{DATA_SET_UUID1}'",
                    f"SELECT param_id from parameters WHERE param_name='{param.name}'",
                    str_repr_index(idx),
                    pyo.value(param[idx]),
                )
                + ")"
                for idx in param.keys()
            )
            + ";\n\n"
        )

    for name in model.component_map(pyo.Set):
        _set = getattr(model, name)

        if _set.is_indexed():
            raise NotImplementedError("TODO indexed sets")
        else:
            ostream.write(
                "INSERT OR IGNORE INTO set_data(data_set_id,set_id,index_str,value)\nVALUES\n"
                + ",\n".join(
                    "\t("
                    + "\n\t\t({}),\n\t\t({}),\n\t\t'{}',\n\t\t'{}'\n\t".format(
                        f"SELECT data_set_id from data_sets WHERE data_set_uuid1='{DATA_SET_UUID1}'",
                        f"SELECT set_id from sets WHERE set_name='{_set.name}'",
                        "None",
                        str(_member).replace("'", "''"),
                    )
                    + ")"
                    for _member in _set
                )
                + ";\n\n"
            )

    _insert_into_files(
        ostream, filename, "data", _id=DATA_SET_UUID1, file_archive=file_archive
    )


def _insert_or_ignore_solution(
    ostream, model: pyo.ConcreteModel, filename: str, file_archive: str
):
    # meta = model.solutions[0]._metadata  # data["Solution"][1]

    results = SolverResults()
    results.read(filename=filename)

    data = results.json_repn()

    ostream.write(
        "INSERT OR IGNORE INTO solutions(data_set_id,solution_uuid1,sol_message,sol_status,objective,gap,time_seconds) \n"
        + "VALUES(\n\t(\n\t\tSELECT data_set_id from data_sets\n\t\tWHERE data_set_uuid1='{}'\n\t),\n\t'{}',\n\t'{}',\n\t'{}',\n\t{},\n\t{},\n\t{}\n);\n\n".format(
            DATA_SET_UUID1,
            SOLUTION_UUID1,
            data["Solver"][0]["Message"],
            data["Solver"][0]["Termination condition"],
            list(data["Solution"][1]["Objective"].values())[0]["Value"],
            (
                "NULL"
                if data["Solution"][1]["Gap"] == "None"
                else data["Solution"][1]["Gap"]
            ),
            data["Solver"][0]["Time"],
        )
    )

    for name in model.component_map(pyo.Var):
        var = getattr(model, name)

        ostream.write(
            "INSERT OR IGNORE INTO variable_data(solution_id,var_id,index_str,value)\nVALUES\n"
            + ",\n".join(
                "\t("
                + "\n\t\t({}),\n\t\t({}),\n\t\t'{}',\n\t\t{}\n\t".format(
                    f"SELECT solution_id from solutions WHERE solution_uuid1='{SOLUTION_UUID1}'",
                    f"SELECT var_id from variables WHERE var_name='{var.name}'",
                    str_repr_index(idx),
                    pyo.value(var[idx]),
                )
                + ")"
                for idx in var.keys()
            )
            + ";\n\n"
        )

    _insert_into_files(
        ostream, filename, "sol", _id=SOLUTION_UUID1, file_archive=file_archive
    )


def _insert(args):

    config = _get_config()

    dbfile = pathlib.Path(config["sqlite3"].get("file", None))
    if dbfile is None:
        raise ValueError("No legal file name for sqlite3['file']")

    file_archive = pathlib.Path(config["archive"].get("directory", None))
    if file_archive is None:
        raise ValueError("No legal name for file_archive.directory")

    model = _get_model(
        model_file=pathlib.Path(args.MODEL).resolve(),
        datacmd_file=pathlib.Path(args.DATA).resolve(),
    )

    _load_solution(model, sol_file=pathlib.Path(args.SOL).resolve())

    # param_set_id = uuid.uuid3(uuid.NAMESPACE_OID, "param_set")

    with io.StringIO() as f:
        _insert_or_ignore_model(
            f,
            model,
            "nlp",
            True,
            pathlib.Path(args.MODEL).resolve(),
            file_archive=file_archive,
        )
        _insert_or_ignore_data_set(
            f, model, pathlib.Path(args.DATA).resolve(), file_archive=file_archive
        )
        _insert_or_ignore_solution(
            f, model, pathlib.Path(args.SOL).resolve(), file_archive=file_archive
        )

        sql = f.getvalue()

    with open("log.txt", "w") as f:
        f.write(sql)

    with sqlite3.connect(dbfile) as con:
        cur = con.cursor()
        cur.executescript(sql)


#     if param.is_indexed():
#         index = param.index_set()

#         # individual index sets into index_sets
#         if isinstance(index, pyomo.core.base.set.SetProduct):
#             for s in index.subsets():  # index._sets
#                 _insert_or_ignore_index(ostream, s)
#                 ostream.write("INSERT OR IGNORE INTO multi_index ()")
#         else:
#             _insert_or_ignore_index(ostream, index)
