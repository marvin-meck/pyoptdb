CREATE TABLE models(
    model_id INTEGER PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_class TEXT CHECK(model_class IN ('lp','milp','nlp','minlp')),
    model_is_convex INTEGER NOT NULL CHECK(model_is_convex IN (0, 1)),
    description TEXT,
    UNIQUE (model_name)
);


CREATE TABLE parameters(
    param_id INTEGER PRIMARY KEY,
    model_id INTEGER NOT NULL,
    param_name TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (model_id) REFERENCES models(model_id),
    UNIQUE (model_id,param_name)
);


CREATE TABLE sets(
    set_id INTEGER PRIMARY KEY,
    model_id INTEGER NOT NULL ,
    set_name TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (model_id) REFERENCES models(model_id),
    UNIQUE (model_id,set_name)
);


CREATE TABLE variables(
    var_id INTEGER PRIMARY KEY,
    model_id INTEGER NOT NULL,
    var_name TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (model_id) REFERENCES models(model_id),
    UNIQUE (model_id,var_name)
);


CREATE TABLE data_sets(
    data_set_id INTEGER PRIMARY KEY,
    model_id INTEGER NOT NULL,
    data_set_uuid1 TEXT NOT NULL UNIQUE,
    FOREIGN KEY (model_id) REFERENCES models(model_id)
);


CREATE TABLE parameter_data(
    param_data_id INTEGER PRIMARY KEY,
    data_set_id INTEGER NOT NULL,
    param_id INTEGER NOT NULL,
    index_str TEXT,
    value REAL,
    FOREIGN KEY (data_set_id) REFERENCES data_sets(data_set_id),
    FOREIGN KEY (param_id) REFERENCES parameters(param_id)
);


CREATE TABLE set_data(
    set_data_id INTEGER PRIMARY KEY,
    data_set_id INTEGER NOT NULL,
    set_id INTEGER NOT NULL,
    index_str TEXT,
    value TEXT,
    FOREIGN KEY (data_set_id) REFERENCES data_sets(data_set_id),
    FOREIGN KEY (set_id) REFERENCES sets(set_id)
);


CREATE TABLE solutions(
    solution_id INTEGER PRIMARY KEY,
    -- model_id INTEGER,
    data_set_id INTEGER NOT NULL,
    solution_uuid1 TEXT NOT NULL UNIQUE,
    sol_message TEXT,
    sol_status TEXT,
    objective REAL,
    gap REAL,
    time_seconds REAL,
    -- FOREIGN KEY (model_id) REFERENCES models(model_id),
    FOREIGN KEY (data_set_id) REFERENCES data_sets(data_set_id)
);

CREATE TABLE variable_data(
    var_data_id INTEGER PRIMARY KEY,
    solution_id INTEGER NOT NULL,
    var_id INTEGER NOT NULL,
    index_str TEXT,
    value REAL,
    FOREIGN KEY (solution_id) REFERENCES solutions(solution_id),
    FOREIGN KEY (var_id) REFERENCES variables(var_id)
);


CREATE TABLE files(
    file_id INTEGER PRIMARY KEY,
    file_location TEXT,
    md5_checksum TEXT NOT NULL UNIQUE,
    file_kind TEXT CHECK(file_kind IN ('sol','data','model')),
    file_type TEXT
);

CREATE TABLE model_has_file(
    model_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    FOREIGN KEY (model_id) REFERENCES models(model_id),
    FOREIGN KEY (file_id) REFERENCES files(file_id)
);

CREATE TABLE solution_has_file(
    solution_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    FOREIGN KEY (solution_id) REFERENCES solutions(solution_id),
    FOREIGN KEY (file_id) REFERENCES files(file_id)
);

CREATE TABLE data_set_has_file(
    data_set_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    FOREIGN KEY (data_set_id) REFERENCES data_sets(data_set_id),
    FOREIGN KEY (file_id) REFERENCES files(file_id)
);
