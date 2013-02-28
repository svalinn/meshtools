#! /usr/bin/env python

# This file requires python >= 2.6 

from itaps import iBase,iMesh
import numpy
import numpy.linalg.linalg as la
import sys, math
import itertools, operator, optparse, operator, textwrap
from contextlib import closing

# Taken from MOAB/src/MBCNArrays.hpp; the canonical numbering is not available through ITAPS/PyTAPS
tet_connect = [ [0,1,3], [1,2,3], [0,3,2], [0,2,1] ]

def loadmesh( filename ):
    mesh = iMesh.Mesh()
    mesh.load( filename )
    cells = list()
    surfs = dict()
    surfcount = 0
    cellcount = 0

    # iterate over cells, creating surface numbers for each triangle
    for i in mesh.iterate( iBase.Type.region, iMesh.Topology.tetrahedron ):

        cellcount += 1

        vertices = mesh.getEntAdj(i, iBase.Type.vertex) 
        cell = list()
        
        # for each triangle in this tet
        for verts in [vertices.take(i) for i in tet_connect]:

            ent_idx = [(e,i) for i,e in enumerate(verts)]
            ent_idx = sorted( ent_idx, key=repr )

            # vkey: a tuple of the triangle's 3 vertices in sorted order by EntityHandle.
            #       This is used as a unique ID for the surface associated with these vertices.
            vkey = tuple( [ e for e,i in ent_idx ] )

            # idxs: an index map of the vkey such that vkey.take(idxs) produces the list of
            #       vertices in the same order as they appear in this triangle.  
            #       This is used to determine the triangle's outward-facing normal relative to 
            #       a cell that contains it.
            idxs = tuple( [ i for e,i in ent_idx ] )

            if vkey not in surfs:
                surfcount += 1
                surfs[vkey] = [surfcount,1]
            else:
                surfs[vkey][1] += 1
            cell.append( (vkey,idxs) )

        cells.append( (cellcount, cell) )

            
    # iterate over surfaces, pulling out vertex data and setting up surfs_out
    surfs_out = list()
    for (vkey,(surf_idx,count)) in surfs.iteritems():
        coords = mesh.getVtxCoords( vkey )
        surfs_out.append( [surf_idx, coords] )


    # sort surfaces according to surface ID; this allows surfs_out to be indexed by (surf_idx-1)
    # in the loop below
    surfs_out.sort( key=operator.itemgetter(0) )

    
    cells_out = list()
    complement_slist = list()

    epsilon = 1e-12

    # iterate over cells again, determining surface sense for each triangle
    for (cellid, cell) in cells: 

        slist = list()

        for (vkey,idxs) in cell:

            surf_idx, scount = surfs[vkey] 
            _, coords = surfs_out[ surf_idx-1 ]
            p1, p2, p3 = coords.take( idxs, axis=0 )

            # unit normal of triangle facing out of cell
            normal = numpy.cross( p2-p1, p3-p1 )
            normal = normal / la.norm( normal )
            
            # vertex furthest from origin
            furthest = max( (p1,p2,p3), key=la.norm )
            # distance from origin to triangle's plane
            D = furthest.dot( normal )
            
            sense = 0

            if( D < -epsilon ):
                sense = 1
            elif( D > epsilon ):
                sense = -1
            else:
                # MCNP sense rules for planes that intercept the origin:
                # if D=0, the point (0,0,infinity) has positive sense
                # if the plane intercepts that point, then (0,infinity,0) has positive sense 
                # if the plane intercepts both points, then (infinity,0,0) has positive sense
                idx = 2
                while sense == 0 and idx >= 0:
                    # Use this dimension if normal[idx] is not zero. 
                    # Note that -0 is not uncommon for axis-aligned planes
                    if abs(normal[idx]) > epsilon: 
                        sense = -int(math.copysign( 1, normal[idx] ))
                    idx -= 1

            if sense == 0:
                print "Error: could not determine the sense of surface", surf_idx
                # The value 0 will be appended to the slist (mcnp5 will choke)

            slist.append( surf_idx * sense )

            # check if surface has only one reference; if so, add it to the complement cell
            if scount == 1:
                complement_slist.append( str(surf_idx * -sense) )
                complement_slist.append( ':' )

        slist.append( 'imp:n=1' )
        cells_out.append( (cellid,slist) )

    complement_slist.pop() # remove the last ':'
    complement_slist.append( 'imp:n=0 $ complement vol ' )
    cells_out.append( (cellid+1, complement_slist ) )

    return (cells_out, surfs_out) 

def writemcnp( cells, surfs, options ):
    with closing( open(options.output_file,'w') ) as out:

        mat = '0'
        if( options.material ):
            mat = '1 '+ str(options.rho)

        # printline function to wrap long lines in MCNP5-compatible syntax
        wrapper = textwrap.TextWrapper( width=68, subsequent_indent='     ' )
        def printline( line ):
            for subline in wrapper.wrap(line):
                print >>out, subline
        
        printline( "mesh2mcnp output" )
        printline( "c BEGIN CELL CARDS" )
        idx = 0
        for cellid, slist in cells:
            printline( ' '.join( [str(s) for s in [cellid,mat]+slist ] ) )


        printline( "c END CELL CARDS" )
        print >>out # newline
        printline ("c BEGIN SURFACE CARDS" )
        
        for surf_idx, coords in surfs:
            printline( str(surf_idx) + ' p ' + ' '.join( [str(s) for s in coords.flat ] ) )


        printline( "c END SURFACE CARDS" )
        print >>out # newline
        printline( "c BEGIN DATA CARDS" )
        
        # add all cells except complement cell to tally F4, plus T for total bucket
        printline( 'F4:n ' + ' '.join( [str(cellid) for cellid,_ in cells[:-1] ] ) + ' T' )        
        printline( "sdef pos 0 0 0" )

        if options.material:
            printline( 'm1 1001 2 8016 1 ' )
        else:
            printline( 'void ' ) 

    return




def main():

    default_output_file = 'mesh2mcnp_output.inp'
    default_rho = -1

    parser = optparse.OptionParser(usage='usage: %prog [options] inputmesh')

    parser.add_option( '-m', '--material', action='store_true', default=False,
                       help='Assign a material to cells (will create m1 as water)' )
    parser.add_option( '--rho', default=default_rho,
                       help='Assign a density value for each cell.  Density is only assigned '
                             'if the -m option is given.  (default %default)')
    parser.add_option( '-o', '--output', dest='output_file', default=default_output_file,
                       help='Output file to create (default %default)' )


    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error( 'Incorrect number of arguments' )

    (cells, surfs) = loadmesh( args[0] )
    writemcnp( cells, surfs, options )


if __name__ == '__main__':

    main()



