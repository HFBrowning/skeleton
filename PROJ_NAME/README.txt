A readme to describe the contents of 'PROJ_NAME'
Hilary Browning

Description


top-level folder
----------------

- __init__.py::  an empty script that allows the folder to be treated as a package
- arcpy_logging.py:: contains a class to convert arcpy GetMessages() into logging module messages
- data.py:: contains data and no programming logic
- main.py:: the main script for running the process
- util.py:: utility helper functions. Contains no arcpy calls, which allows it to be tested more easily by unit testing (in the tests folder)



logs
----
This folder is where logs are written to during a run. 
