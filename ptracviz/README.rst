ptracviz
========
Script last updated ~6-2009.
- original author B. Kiedrowski
- C++ script that takes an MCNP ptrac file and converts it to a journal
  file for CUBIT for track visualization.
- Current testing shows functionality on raw tracks, source points, and
  surface crossing events.
- All options may not be functional and script may need to upgraded to
  accommodate these.

Guide from code comments
========================
This is a tool designed to parse a ptrac file from MCNP and
convert it to a journal file in CUBIT for visualization.::
    v1.0 -- Initial release
    v1.1 -- Improvements in logic, fixed some a bug so that
            now individual event points can be displayed

Known issues
------------
Coloring of tracks and vertices is done by particle type
unfortunately, it appears the location of this info moves
depending on the data requested.  Need improvement in logic
to address this.

Usage
-----
::
    ./a.out [ptrac file] [journal file]

defaults are "ptrac" and "ptr.jou" respectively
