# Advance Parser Design Document

In [Building Templates](./BuildingTemplates.md), we went through the processDB tags for 
parameters that can change. We started with the assumption that the template correctly
configured the devices, and only the 'network parameters' needed to be changed. Because of 
this we only needed the 'basic parser' to build the final configuration file.

We also assumed that the equipment on the 'Site' was consistent, allowing for example 
the Sector Template to be used for all sectors on the site. But what if this is not the
case? What if different equipment is used for different sectors, PTP connections or Client 
Connections. In this case we need must customize the hardware configuration for the different
pieces of equipment, requiring different templates, or other ways to customize the
configuration file.

If we look at our template files we see a structure of command, action and parameters,
with the parameters being name value pairs, and we made use of the name value pairs for our 
substitution. Essentially we have what is known as a 'flat' .ini file (one with no
categories). What we need to solve our problem is a more complicated structure which allow
us to select our name value pairs, based on equipment type.

## Markup Language
Markup Languages allow you to describe data, in a structured way, using name values pairs.
Example of markup languages are XML, JSON, YAML, HCL, ... There are many advantages and
disadvantages to each markup language, and the choice of which one to useis not only based
on requirements, but on preference. In our case we want a markup language than has strong 
library support for encoding and decoding, and can be stored and understood by the database.
So the language we have chosen is JSON, for our advance template tool.

## Slicing our Template file into JSON Snippets
