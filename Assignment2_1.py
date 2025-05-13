#SIOULAS ALEXANDROS AM: 5349
import sys

############################################################# 

def read_coords(coords_filename):
    coords = []
    with open(coords_filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(',')
                x = float(parts[0])
                y = float(parts[1])
                coords.append((x, y))
    return coords

def read_offsets(offsets_filename):
    offsets = []
    with open(offsets_filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(',')
                obj_id = int(parts[0].strip())
                start = int(parts[1].strip())
                end = int(parts[2].strip())
                offsets.append((obj_id, start, end))
    return offsets

############################################################# 

def interleave_latlng(lat, lng, bits=32):
    
    x = int((lng + 180) / 360 * (2**bits - 1))
    y = int((lat + 90) / 180 * (2**bits - 1))
    
    result = 0
    
    for i in range(bits - 1, -1, -1):
       
        result = (result << 1) | ((x >> i) & 1)
        result = (result << 1) | ((y >> i) & 1)
    return format(result, '0{}x'.format(bits // 4))

def compute_mbr(points):
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    return [min_x, max_x, min_y, max_y]

def union_mbrs(mbr_list):
    min_x = min(m[0] for m in mbr_list)
    max_x = max(m[1] for m in mbr_list)
    min_y = min(m[2] for m in mbr_list)
    max_y = max(m[3] for m in mbr_list)
    return [min_x, max_x, min_y, max_y]

############################################################# 

def partition_entries(entries, capacity, min_entries):
    groups = []
    i = 0
    n = len(entries)
    
    while i < n:
        group = entries[i:i+capacity]
        groups.append(group)
        i += capacity

    # if there is more than one group (not root) and the last group has less than the minimum number of entries (8) we adjust by moving elements from the previous group
    if len(groups) > 1 and len(groups[-1]) < min_entries:

        move_set = min_entries - len(groups[-1])
        
        # move entries from second-to-last to the last
        moved_entries = groups[-2][-move_set:]
        groups[-2] = groups[-2][:-move_set]

        # add to the begining of the last group
        groups[-1] = moved_entries + groups[-1]

    return groups

def create_nodes_from_entries(entries, is_leaf, capacity, min_entries, global_node_id):
    
    nodes = []
    groups = partition_entries(entries, capacity, min_entries)
    for group in groups:
        # nodes MBR as the union of the MBRs of all the entries in the group
        mbrs = [entry[1] for entry in group]
        node_mbr = union_mbrs(mbrs)

        # 0 = leaf, 1 = non-leaf 
        node_flag = 0 if is_leaf else 1

        # nodes entries [id, MBR] 
        node_entries = [[entry[0], entry[1]] for entry in group]

        node = (node_flag, global_node_id, node_entries, node_mbr)
        nodes.append(node)

        global_node_id += 1

    return nodes, global_node_id

def build_rtree(leaf_entries, capacity=20, min_entries=8):
    global_node_id = 0
    levels = []  
    
    # create leaf node, each contains entries of the form object_id, MBR
    leaf_nodes, global_node_id = create_nodes_from_entries(leaf_entries, True, capacity, min_entries, global_node_id)
    levels.append(leaf_nodes)
    current_level = leaf_nodes
    
    # recursively build non-leaf levels
    while len(current_level) > 1:
        # for each node create an entry for the parent level
        # (child_node_id, mbr)
        parent_entries = [(node[1], node[3]) for node in current_level]
        # create parent nodes (non-leaf nodes) from these entries
        parent_nodes, global_node_id = create_nodes_from_entries(parent_entries, False, capacity, min_entries, global_node_id)
        levels.append(parent_nodes)
        current_level = parent_nodes
    return levels

############################################################# 

def write_rtree_file(levels, output_filename="Rtree.txt"):
    all_nodes = []
    for lvl in levels:
        all_nodes.extend(lvl)
    # sort by node_id
    all_nodes.sort(key=lambda node: node[1])
    with open(output_filename, 'w') as f:
        for node in all_nodes:
            # [isnonleaf, node_id, entries]
            line = f"{[int(node[0]), node[1], node[2]]}\n"
            f.write(line)
    print("R-tree written to file \"Rtree.txt\".\n")

############################################################# 

def main():

    if len(sys.argv) != 3:
        print("Use: Assignment2_1.py <coords_file> <offsets_file>")
        # python Assignment2_1.py coords.txt offsets.txt  
        sys.exit(1)

    coords_file = sys.argv[1]
    offsets_file = sys.argv[2]

    coords = read_coords(coords_file)
    offsets = read_offsets(offsets_file)
    
    # for each polygon compute its MBR & z-order value
    leaf_entries = []
    for (obj_id, start, end) in offsets:
        # sublist from coords including both start and end
        points = coords[start:end+1]
        mbr = compute_mbr(points)
        # center of MBR
        center_x = (mbr[0] + mbr[1]) / 2
        center_y = (mbr[2] + mbr[3]) / 2
        # z-order value 
        z_val = interleave_latlng(center_y, center_x)
        leaf_entries.append((obj_id, mbr, z_val))
    
    # z-order value sort
    # sorting key is the hex string returned by interleave_latlng()
    leaf_entries.sort(key=lambda entry: entry[2])
    
    # remove z-order value (object_id, MBR)
    new_leaf_entries = []
    for entry in leaf_entries:
        obj_id, mbr, _ = entry
        new_leaf_entries.append((obj_id, mbr))

    # R-tree 
    levels = build_rtree(new_leaf_entries, capacity=20, min_entries=8)

    print("------------------------------------------------------------")
    # write R-tree
    write_rtree_file(levels, output_filename="Rtree.txt")
    
    # number of nodes per level 
    print("Number of Nodes per level:")
    for level_index, level_nodes in enumerate(levels):
        print(f"{len(level_nodes)} nodes at level {level_index}")
    print("------------------------------------------------------------")

   

if __name__ == '__main__':
    main()
