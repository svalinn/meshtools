mesh2mcnp
=========
Last updated ~7/2011

mesh2mcnp.py is a PyTAPS-based tool to convert a tet mesh into an MCNP5 input.

This script's output is an mcnp5 input file describing an MCNP cell for each 
tetrahedron  in the input mesh.  A single f4 tally is also created, with one 
tally bucket per cell.  This script is intended to be a testing tool for 
conformal mesh tallies.

The limiting factor of this script is the number of surface triangles on the
input mesh.  Above about 500 triangles, MCNP5 will reject the "rest-of-world" 
cell created by this script as having too many input tokens.

This version of the script lacks a command-line interface, and the input file
must be chosen by editing the bottom of the file.  The default is tetbrick.cub,
an included test file.


Usage
=====
Can be called from the command line, with various options.  Use::
    ./mesh2mcnp.py -h

for more information.


