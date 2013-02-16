Intro
-------
This folder contains the script `tet_vals_and_centroids.py`, which loads a MOAB mesh file (e.g. .vtk or .h5m file), calculates the centroid of any tetrahedron elements, and writes the x,y,z plus tally values and errors to a file.

Dependencies
------------
Script requires that itaps/pytaps is installed.

Optional plotting feature requires matplotlib.

Usage
-------
Call the script as ::
  ./tet_vals_and_centroids.py inputfile.vtk

There are several options that can be passed to the script as well. Use the `-h` flag to learn more.

The default output file is `tet_centers_output`.

By default, the mesh is searched for the tags 'TALLY_TAG' and 'ERROR_TAG'.
