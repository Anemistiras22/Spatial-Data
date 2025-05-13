#SIOULAS ALEXANDROS AM: 5349
import sys
import heapq

############################################################# 

def load_rtree(filename):
    rtree = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.strip():
                node = eval(line.strip())
                isnonleaf = node[0]
                node_id = node[1]
                entries = node[2]
                rtree[node_id] = (isnonleaf, entries)
    return rtree

def load_nn_queries(filename):
   
    queries = []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split()
                x, y = map(float, parts)
                queries.append((x, y))
    return queries

############################################################# 

def point_to_rect_dist(q, rect):
    
    x, y = q
    x_low, x_high, y_low, y_high = rect
    dx = 0
    if x < x_low:
        dx = x_low - x
    elif x > x_high:
        dx = x - x_high
    dy = 0
    if y < y_low:
        dy = y_low - y
    elif y > y_high:
        dy = y - y_high
    
    return dx * dx + dy * dy

def union_mbr(entries):

    #(child_id, (x_low, x_high, y_low, y_high))
    x_low = min(entry[1][0] for entry in entries)
    x_high = max(entry[1][1] for entry in entries)
    y_low = min(entry[1][2] for entry in entries)
    y_high = max(entry[1][3] for entry in entries)
    return (x_low, x_high, y_low, y_high)

def knn_query(rtree, root_id, q, k):
   
    results = []
    heap = []
    # for the root calculate its overall MBR as the union of all entries
    root_isnonleaf, root_entries = rtree[root_id]
    root_mbr = union_mbr(root_entries)
    # calculate distance from q to the root MBR
    d = point_to_rect_dist(q, root_mbr) 
    # heap (distance, type, id, mbr)
    # type = 0 -> node,  1 -> object (leaf entry)
    heapq.heappush(heap, (d, 0, root_id, root_mbr))

    # while the heap is empty or we have found k objects
    while heap and len(results) < k:
        d, typ, ident, mbr = heapq.heappop(heap)
        if typ == 1:
            # entry is a leaf entry -> add id to results 
            results.append(ident)
        else:
            # entry is a node 
            node_isnonleaf, entries = rtree[ident]
            for child in entries:

                child_id, child_mbr = child
                # current node
                # or isnonleaf == 1, children are nodes -> (type 0)
                # or isnonleaf == 0, children are objects -> (type 1)
                child_type = 0 if node_isnonleaf == 1 else 1
                # calculate the distance from the query point q to the childs MBR
                d_child = point_to_rect_dist(q, child_mbr)
                # add the child entry to the heap
                heapq.heappush(heap, (d_child, child_type, child_id, child_mbr))
    return results


############################################################# 

def main():
    
    if len(sys.argv) != 4:
        print("Use: python Assignment2_3.py <Rtree_file> <NNqueries_file> <k>") 
        # python Assignment2_3.py Rtree.txt NNqueries.txt 10
        sys.exit(1)
    
    rtree_file = sys.argv[1]
    nn_queries_file = sys.argv[2]
    k = int(sys.argv[3])
    
    rtree = load_rtree(rtree_file)
    
    # find root_id by reading the last line
    with open(rtree_file, "r") as f:
        lines = [line for line in f if line.strip()]
    root = eval(lines[-1].strip())
    root_id = root[1]
    
    # NN_queries
    queries = load_nn_queries(nn_queries_file)
    
    # write results
    with open("nn_query_results.txt", "w") as fout:
        for idx, q in enumerate(queries):
            knn = knn_query(rtree, root_id, q, k)
    
            fout.write(f"{idx}: {','.join(str(x) for x in knn)}\n")
    print("------------------------------------------------------------")
    print("\nResults written to file \"nn_query_results.txt\".\n")
    print("------------------------------------------------------------")
    
        

if __name__ == "__main__":
    main()
