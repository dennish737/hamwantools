# Basic Parser Design Document
## Goals
 1) Read a 'text' template
 2) Substitute Template Names with Database Value 
 3) Generate a Mikrotik .rsc file 

### Dealing with missing parameters
Since we are pulling parameters from a database, and the parameters are 
columns in tables, parameters that have no value will return as NULL, which python 
converts to None. If a Template name, has no corresponding value in the Database,
a text string of 'None' will be substituted., and a warning will be generated.

### Dealing with bad templates
Templates are text files, consisting of Mikrotik commands, actions and parameters.
Furthermore, parameters are name value pairs. Unfortunately, there is no way,
for the basic_parser tool, to verify that the template used is correct, and 
contains no errors. One should always check the output file for errors.

## How does it work?
Let's assume that we have a valid template, with correctly substituted 'Template_name'
as describe in [BuildingTemplates.md](./BuildingTemplates.md). We will also need to know 
the 'organization name', site name, and the device name (e.g. organization = spokane,
site = Krell and device = r1.KRELL). Finally, we will need to know the file name for the
database.

The organization, site and device names are used to look up the Global, Security and 
device 'parameters' for the device, and build a parameter dictionary of name value pairs.

We then open the template file, and process each line, by splitting the line into key/value
pairs and using the mapping tables (map_table.py) to map the Template_name to the 
Database Name,and substitute the database value for the Template_name. If the value part 
is not one of the defined Template_names, the original value is used. Once the line is
processed, we re-assemble the line, and write it to the .rsc file. 

The application also generate a log file, which can be used to locate and trouble shoot problems.

## Running the code
We are assuming that you have downloaded the git archive for the tool and cd to the hamwantools root
directory (.../hamwantools), and set up the python environment.

```commandline
 python ./tools/basic_parser.py [Options]
 
 Example:
 python ./tools/basic_parser.py -c spokane, --db ../data/spokane_example.sqlite3 --device r1.KRELL --site krell ../templates/r_router_template.txt
```

