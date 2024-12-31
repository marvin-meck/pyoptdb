# pyoptdb (Pre-alpha)

`pyoptdb` is a data management utility for [Pyomo](https://github.com/marvin-meck/pyomo) users. 
`pyoptdb` is used to create a disk-based database containing model and solution data. 
The database engine used is [SQLite](https://www.sqlite.org) which is interfaced using the [`sqlite3`](https://docs.python.org/3/library/sqlite3.html) `Python` module. 
This allows the user to efficiently query solution data using SQL. 

`pyoptdb` provides the following sub-commands:
- Configure: `pyoptdb config`
- Initialize: `pyoptdb init`
- Insert: `pyoptdb insert`

## Configure

When running `pyoptdb` for the first time a *global* configuration file will saved in your user home path in a subdirectory `.pyoptdb`. 
`pyoptdb` can be configured *locally* by invoking 

```shell
pyoptdb config option value
```

To view a list of the current configuration type
```shell
pyoptdb config --list
```

## Initialize 

Initialize a new repository. 
The command 
```shell
pyoptdb init
```
creates an empty database file from the default schema and also creates the directory for the file-archive. 

## Insert

Insert solutions into the database.
Use 
```shell
pyoptdb insert --help
```
for help. 