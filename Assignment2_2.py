#SIOULAS ALEXANDROS AM: 5349
import sys


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

def load_queries(filename):

    queries = []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split()
                x_low, y_low, x_high, y_high = map(float, parts)
                queries.append((x_low, x_high, y_low, y_high))
    return queries

############################################################# 

def rects_intersect(r1, r2):

    # r1 & r2  (x_min, x_max, y_min, y_max)
    x1_min, x1_max, y1_min, y1_max = r1
    x2_min, x2_max, y2_min, y2_max = r2

    #intersection
    if x1_max < x2_min or x1_min > x2_max:
        return False
    if y1_max < y2_min or y1_min > y2_max:
        return False

    return True

def range_query(rtree, node_id, query_rect):
    results = []
    isnonleaf, entries = rtree[node_id]         # 0 = leaf, 1 = non-leaf 
    for child_id, mbr in entries:
        if rects_intersect(mbr, query_rect):  # if intersection
            if isnonleaf:  
                #continue recur
                results.extend(range_query(rtree, child_id, query_rect))
            else: 
                #append obj id 
                results.append(child_id)

    return results

############################################################# 

def main():

    if len(sys.argv) != 3:
        print("Use: python Assignment2_2.py.py <Rtree_file> <queries_file>")
        # python Assignment2_2.py Rtree.txt Rqueries.txt  
        sys.exit(1)
    
    rtree_file = sys.argv[1]
    queries_file = sys.argv[2]
    
    rtree = load_rtree(rtree_file)
    
    # find root_id by reading the last line
    with open(rtree_file, 'r') as f:
        lines = [line for line in f if line.strip()]
    root = eval(lines[-1].strip())
    root_id = root[1]
    
    #R_queries
    queries = load_queries(queries_file)
    
    # write results
    with open("range_query_results.txt", "w") as fout:
        for idx, q in enumerate(queries):
            results = range_query(rtree, root_id, q)
            fout.write(f"{idx} ({len(results)}): {','.join(str(x) for x in results)}\n")
    print("------------------------------------------------------------")   
    print("\nResults written to file \"range_query_results.txt\".\n")
    print("------------------------------------------------------------")
    
        
if __name__ == "__main__":
    main()
