meshtools
=========

Scripts/tools for working with various nuclear-related tools and MOAB/iTaps based structured and unstructured meshes.

Tools
-----

- `lostparticles/` contains
   - `mklostvis.pl` which parses MCNP output file to create a CUBIT .jou file for visualizing lost particle locations.
   - `lostparts2mesh.py` which parses an MCNP output file to create a MOAB mesh file for visualizing lost particle locations.
- `mesh2mcnp/` contains `mesh2mcnp.py` which creates an MCNP input from a (small) tet mesh.
- `ptracviz/` contains `ptracviz.cpp` which takes an MCNP ptrac file and converts it to a journal file for visualizing tracks in CUBIT.
- `tetmesh2points/` contains the script `tet_vals_and_centroids.py`, which loads a MOAB mesh file (e.g. .vtk or .h5m file), calculates the centroid of any tetrahedron elements, and writes the x,y,z plus tally values and errors to a file.
