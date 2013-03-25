#! /usr/bin/env python
"""This script deletes tags from a MOAB mesh.

Regular expressions (python flavored) can be used to delete a bunch of similar
tags.

Optionally, a third parameter with the output file name can be supplied. By default the source file for the mesh is modified.
"""

from itaps import iMesh, iBase
#from r2s.scdmesh import ScdMesh
from optparse import OptionParser
import sys
import re


def main(filename, tagstring, outputname=None):
    """Load mesh
    """
    tagstring = tagstring.lower()

    if not outputname: outputname=filename

    mesh = iMesh.Mesh()
    print "Attempting to load {0}".format(filename)
    #try: #This should work fine for mesh files containing an ScdMesh.
    mesh.load(filename)
    print "Successfully loaded mesh."
    #except iBase.NotSupportedError:
    #    sm = ScdMesh.fromFile(filename)
    #    mesh = ScdMesh.imesh
    #    print "Successfully loaded mesh from an ScdMesh."
        

    # Grab first voxel entity on mesh, from which we get voxel-level tag handles
    for x in mesh.iterate(iBase.Type.region, iMesh.Topology.all):
            break
                    
    handles = mesh.getAllTags(x)

    for handle in handles:
        tagname = handle.name.lower()
        if re.findall(tagstring, tagname):
            print "Deleting tag {0}".format(tagname)
            mesh.destroyTag(handle, force=True)

    print "Saving mesh."
    mesh.save(filename)


if __name__ == "__main__":

    usage = "%prog <mesh file> <regex-string-tagname-to-delete>" \
            "(optional: <output file name>)"
    usageNotes = "\n\nThe regex/delete string is case insensitive.\n" \
            "An example reg-ex which will delete all photon source tags:\n" \
            "  'phtn_src_group_[0-9]{3}'"
    parser = OptionParser(usage + usageNotes)

    (opts, args) = parser.parse_args(sys.argv)

    if len(args) < 3:
        print "Must pass file name and a tagname/regex expression to delete."
        print usage
    elif len(args) == 3:
        main(args[1], args[2])
    else:
        main(args[1], args[2], args[3])
