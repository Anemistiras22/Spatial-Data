# Spatial-Data
The goal of this task was to construct and use an R-tree index for spatial data.

Complex Data Management MYE041 CSE-UOI 2025

Assignment 2

SIOULAS ALEXANDROS ID: 5349

Introduction:

The goal of this assignment was to construct and utilize an R-Tree index for spatial data, using the bulk loading technique and a space-filling curve (z-order curve). Additionally, range queries and k-Nearest Neighbor (kNN) queries were performed on the R-tree.
The implementation was done in Python.

Implementation Description:

Part 1: R-Tree Construction with Bulk Loading

The R-Tree construction included the following steps:

Reading Data:

The read_coords function reads point coordinates from the file coords.txt.

The read_offsets function reads polygon offsets from the file offsets.txt, which define the points of each polygon.

MBR and Z-order Calculation:

The compute_mbr function calculates the minimum bounding rectangle (MBR) for each polygon.

The center of each MBR is converted to a z-order value using the interleave_latlng function, according to the z-order curve.

Sorting and Grouping:

The MBRs are sorted based on their z-order values.

The partition_entries function splits the data into groups, with each group containing between 8 and 20 entries. Elements are shifted if needed to meet the (8 - 20) requirement.

Tree Construction:

The create_nodes_from_entries function creates either leaf or internal nodes.

The build_rtree function recursively builds the R-Tree, from the leaves up to the root.

The tree is saved to the file Rtree.txt using the write_rtree_file function.

The program also prints the number of nodes at each level of the tree.

Part 2: Range Queries

For range queries:

Reading Data:

The load_rtree function reads the R-Tree from Rtree.txt and stores it in a dictionary.

The load_queries function reads the range queries from Rqueries.txt.

Tree Search:

The rects_intersect function checks if two rectangles (MBRs) intersect.

The range_query function performs recursive searching on the R-Tree:

If the node is a leaf, it adds to the results the objects that intersect with the query window.

If the node is internal, the search continues recursively to its children.

The results of each query are written to the file range_query_results.txt, along with the number of results and the IDs of the objects.

Part 3: k-Nearest Neighbor (kNN) Queries

For kNN queries:

Reading Data:

The load_nn_queries function reads the reference points from the file NNqueries.txt.

Search Implementation:

The point_to_rect_dist function computes the squared distance from a point to an MBR.

The union_mbr function is used to calculate the union MBR of a node.

The knn_query function implements the best-first search algorithm:

It uses a heapq to process the closest MBRs first.

When a leaf entry is found, it is added to the results.

When a node is found, its children are added to the queue based on their distance to the reference point.

The results of each query are written to the file nn_query_results.txt, listing the k nearest objects per line.

Execution:

The programs are executed via command line:

python Assignment2_1.py coords.txt offsets.txt
python Assignment2_2.py Rtree.txt Rqueries.txt
python Assignment2_3.py Rtree.txt NNqueries.txt k
