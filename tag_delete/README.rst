Intro
-----
This script deletes tags from a MOAB mesh.

Regular expressions (python flavored) can be used to delete a bunch of similar
tags.

Optionally, a third parameter with the output file name can be supplied. By default the source file for the mesh is modified.

Script last updated 3-24-2013.

Dependencies
------------
Script requires that itaps/pytaps is installed.

Usage
-----
`tag_delete.py` is an executable Python script. It takes 2 to 3 argumets: (1) mesh file name; (2) tag name/regular expression to delete; (3) output file name.

Example invocations::
    ./tag_delete.py mesh.h5m phtn_src_total
    ./tag_delete.py mesh.h5m phtn_src_group[0-9]{3} newmesh.h5m

The latter example uses a regular expression that will match (and delete) all tags with names of the form "phnt_src_group_###".

To learn more about Python's regular expressions, see: http://docs.python.org/2/library/re.html
