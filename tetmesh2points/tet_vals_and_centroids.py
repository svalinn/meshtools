#! /usr/bin/env python

import sys
from optparse import OptionParser
from datetime import datetime

from itaps import iMesh, iBase


def get_centers_and_vals(filename, outfile, valtagname, errtagname, plotnum, \
        header):
    """
    """
    imesh = iMesh.Mesh()

    imesh.load(filename)
    
    cnt = 0

    taltag = imesh.getTagHandle(valtagname)
    errtag = imesh.getTagHandle(errtagname)

    with open(outfile, 'w') as fw:

        # write metadata/comment line
        if header:
            fw.write("# File created: {0}  From: {1}\n".format( \
                    datetime.now().strftime("%D %H:%M"), filename))
            fw.write("# {0:<12}\t{1:<12}\t{2:<12}\t{3:<12}\t{4:<12}\n".format( \
                    "x", "y", "z", "tally", "error"))
    
        # 
        for tet in imesh.iterate(iBase.Type.region, iMesh.Topology.tetrahedron):
            vtxs = imesh.getVtxCoords(imesh.getEntAdj(tet, iBase.Type.vertex))
            # calculate centroid
            centroid = list()
            for idx in xrange(3):
                centroid.append(sum([vtx[idx] for vtx in vtxs])/4.0)

            # Write output
            fw.write("{0:<12}\t{1:<12}\t{2:<12}\t{3:<12}\t{4:<12}\n".format( \
                    centroid[0], centroid[1], centroid[2], \
                    taltag[tet], errtag[tet]))
            
            cnt += 1

            # Optionally plot points of a tet for verification
            if cnt == plotnum:
                print "Example centroid...\n"
                print "For tet with coords\n{0}\n".format(vtxs)
                print "We find the centroid to be:\n{0}\n".format(centroid)
                plot(vtxs, centroid)

    print "{0} tetrahedrons found\nTet center coordinates and tally value/" \
            "errors written to: {1}".format(cnt, outfile)


def plot(vtxs, centroid):
    """Creates 3D scatter plot of vertices and centroid of a single tetrahedron.
    """
    import numpy as np
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt

    fig = plt.figure()

    ax = fig.add_subplot(111, projection='3d')

    xs = [vtx[0] for vtx in vtxs]
    ys = [vtx[1] for vtx in vtxs]
    zs = [vtx[2] for vtx in vtxs]

    centX = centroid[0]
    centY = centroid[1]
    centZ = centroid[2]

    # plotting
    (c, m) = ('r', 'o')
    ax.scatter(centX, centY, centZ, c=c, marker=m)

    (c, m) = ('b', '.')
    ax.scatter(xs, ys, zs, c=c, marker=m)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()


def main():
    """
    """
    usage = "usage: %prog input-moab-file [options]\n\n" \
        "Script reads in a moab file (e.g. .vtk or .h5m), and outputs a file " \
        "listing the centers of all tetrahedron voxels, and the " \
        "corresponding values (e.g. tally and error) tagged to the voxels."
    parser = OptionParser(usage)

    #
    parser.add_option("-o","--output",action="store",dest="outfile", \
            default="tet_centers_output",help="Output file name for " \
            "resulting file. Default: %default")
    #
    parser.add_option("-t","--taltag",action="store",dest="taltag", \
            default="TALLY_TAG",help="Tag name for tally values. " \
            "Default: %default")
    #
    parser.add_option("-e","--errtag",action="store",dest="errtag", \
            default="ERROR_TAG",help="Tag name for error values. " \
            "Default: %default")
    # Include header
    parser.add_option("-H","--header",action="store_false",dest="header", \
            default=True,help="Option disables header line at top of output. " \
            "Default: %default")
    # Visual inspection
    parser.add_option("-p","--plot",action="store",dest="plotnum", \
            default=-1,help="Plot the vertices and centroid of the " \
            "n'th tet. Default: n=-1 (doesn't plot)")

    (options, args) = parser.parse_args()

    get_centers_and_vals(args[0], options.outfile, options.taltag, \
            options.errtag, int(options.plotnum), options.header)
    

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print "must pass a filename."
    else:
        main()
