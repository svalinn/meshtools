
import sys
import numpy as np

uvw_tag_name = "RAY_DIR"
output_filename = "lost_particle_locations.h5m"
#open the mcnp output file
file = open(sys.argv[1], 'rb')
#start with five lines in our line_cache
line_cache = [file.readline(),file.readline(),file.readline(),file.readline(),file.readline(),file.readline()]
#dictionary for holding lost particle info
lost_part_dict = {}
for line in file:
    #add line to cache
    line_cache.append(line)    
    #line_cache should always be size six here
    assert(7 == len(line_cache))
    #check for lost particle indicator substring
    if "no intersection found in subroutine track" in line_cache[0]:
        #lost particle add last known location and number to dictionary
        #need to adjust parsing if more than 100 are lost
        split_key_line = line_cache[0].split()
        key = split_key_line[4] if len(lost_part_dict) < 100 else split_key_line[3].split('.')[-1]
        xyz = line_cache[-2].split()[2:5]
        uvw = line_cache[-1].split()[3:6]
        #add to lost particle dict
        lost_part_dict[key] = xyz + uvw
    #remove line from cache
    line_cache.pop(0)
    
#print out some info for user verification
print("Found" ,len(lost_part_dict), "lost particles.")
print(lost_part_dict["no"])

#write the data to a mesh
try:
    from pymoab import core,types
    mbi = core.Core()
    print("Using pymoab to generate mesh file....")
    ray_tag_handle = mbi.tag_get_handle(uvw_tag_name, 3, types.MB_TYPE_DOUBLE, True)
    #vertices to the MOAB instance
    verts = mbi.create_vertices(np.array([float(i) for l in lost_part_dict.values() for i in l[:3]],dtype='float64'))
    #and now tag the verices with the lost particle directions
    mbi.tag_set_data(ray_tag_handle, verts, np.array([float(i) for l in lost_part_dict.values() for i in l[3:6]]))
    # write the vertex locations to file
    mbi.write_file(output_filename)
    print("Done.")
    sys.exit()
except ImportError:
    pass
try:
    from itaps.iMesh import Mesh
    mbi = Mesh()
    print("Using iMesh to generate mesh file.")        
    #create vertices for each lost particle location
    vertices = []
    for lost_part in lost_part_dict.values():
        vertices.append(mbi.createVtx([float(i) for i in lost_part[:3]]))
        #create a tag for the direction of lost particles
    ray_tag_handle = mbi.createTag(uvw_tag_name,3,'d')
    for vert,lost_part in zip(vertices,lost_part_dict.values()):
        ray_tag_handle[vert] = [float(i) for i in lost_part[3:6]]
    mbi.save(output_filename)
    print("Done.")
    sys.exit()
except ImportError:
    print("No supported mesh modules found. Please install pymoab or iMesh")
