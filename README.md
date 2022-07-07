# Router Config
## Introduction
This project provides a set of tools for the setup and configuration of a Regional HamWAN network

The structure of the project is as follows:
 - Top Level: tools, README, LICENSE, MANAFEST, etc
 - commands: useful Mikrotik 
 - data: parameter database and json config templates
 - doc: documentation and How To
 - doc/images: images used in docs
 - logs : run logs
 - outputs: configuration outputs
 - parsers: 
 - queries: useful database queries
 - venv: python virtual environment

## List of tools
 - config.py: generates device config file, then sends the file to the device

## Prerequists
The following items need t obe installed on the users system:

 - python and pip: can be downloaded from [here](https://www.python.org/).
 - Db View: can be downloaded from [here](https://sqlitebrowser.org/).
 - sqlite: can be downloaded from [here](https://www.sqlite.org/index.html).
 - python virtual environments - This is optional, but recommend. For more information \
   - on python on python environments [see](https://docs.python.org/3/library/venv.html). \
   - Note: If you use environments, you must activate the environment before installing \
   - the required packages
 - python libraries installed: pip install -r requirements.txt (depending on install you many need to use pip3)
 - Optional
    - PyCharm: can be downloaded from [here](https://www.jetbrains.com/pycharm/download/#section=windows).

## Applications

### config.py
Tool to configure a HamWAN device.
Example run command:
   python config.py -s SPODEM.PTP --mode config --dtype PTP

### add_organization.py
Add an organization to te planning db
Multiple organizations can be added using template organization_template.csv

### add_sites.py
Add sites, for an organization, to hte planning DB. Available template site_template.csv

### add_paths.py
Add backbone data paths to the DB


### create_blocks.py
Tool to create ip address blocks.
Example run command:
   python create_blocks.py -c spokane

## Documents
 - First_Time.md - Initial setup of a device
 - HamWAN Background.md
 - UsefulArticals.md - a list of useful articles and videos
 - 