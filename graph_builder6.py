import re
import sys
import heapq

# Make weighted array initialization global
weighted_array = []

def add_node():
    for row in weighted_array:
        row.append(0)
    new_row = [0 for i in range(len(weighted_array) + 1)]
    weighted_array.append(new_row)


def add_edge(start, destination, weight):
    weighted_array[start][destination] = weight


def remove_node(node):
    for rows in weighted_array:
        if rows[node] != 0:
            rows[node] = 0
    weighted_array.pop(node)
    
    
def remove_edge(start, destination):
    weighted_array[start][destination] = 0


def to_adjacency_list():
    i, j = 0 , 0
    fin = [("City"+str(i)+":") for i in range(len(weighted_array))] # c to C for formatting
    first = True
    for rows in weighted_array:
        j = 0  
        for cols in rows:
            if cols != 0:
                if first == True:
                    fin[i] += " City" + str(j) + "(" + str(cols) + ")" # c to C for formatting
                    first = False
                else:
                    fin[i] += ", City" + str(j) + "(" + str(cols) + ")" # c to C for formatting
            j += 1
        first = True
        i += 1
    for routes in fin:
        print(routes)

# Make graph building logic a defined function for reuse
def build_graph(file_path):
    pattern1 = re.compile(r"City(\d+) City(\d+) (\d+)")
    number_of_cities = 0
    number_of_roads = 0
    city_counter_mode = False
    road_counter_mode = False
    for line in file:
        clean_line = line.strip()
        if clean_line == 'CITIES':
            city_counter_mode = True
            continue
        if clean_line == 'ROADS':
            city_counter_mode = False
            road_counter_mode = True
            continue
        if city_counter_mode and clean_line:
            number_of_cities += 1
        if road_counter_mode and clean_line:
            number_of_roads += 1

    weighted_array = [[0 for _ in range(number_of_cities)] for _ in range(number_of_cities)]
    edge_list = []
    file.seek(0)
    road_mode = False
    for line in file:
        clean_line = line.strip()
        match = pattern1.search(clean_line)
        if match:
            start = int(match.group(1))
            destination = int(match.group(2))
            weight = int(match.group(3))
            edge_list.append((start,destination,weight))
            weighted_array[start][destination] = weight

    return weighted_array, edge_list # Add return for reusing populated weighted array elsewhere

# Update traffic from file
def update_traffic(file):
    traffic_pattern = re.compile(r"TRAFFIC_REPORT City(\d+) City(\d+) ([-+]?\d+)")

    for line in file:
        clean_line = line.strip()
        match = traffic_pattern.search(clean_line)
        if match:
            start = int(match.group(1))
            destination = int(match.group(2))
            traffic = int(match.group(3))

            #if traffic update makes travel impossible skip the update
            if (weighted_array[start][destination] + traffic) <= 0:
                weighted_array[start][destination] = 0
            else:   
                weighted_array[start][destination] += traffic

    return weighted_array

# create an edge list for dijkstra's algorithm
def edge_list_to_adjacency_list(edge_list):
    adj_list = {}
    for(src, dest, weight) in edge_list:
        if src not in adj_list:
            adj_list[src] = {}

        adj_list[src][dest] = weight
 
    return adj_list

# dijkstra's function
def dijkstra(adj, file):
    traffic_pattern = re.compile(r"QUERY SHORTEST_PATH City(\d+) City(\d+)")
    results = []
    paths = []
    formatted_results = []
    for line in file:
        # clean and match format
        clean_line = line.strip()
        match = traffic_pattern.search(clean_line)
        if match:
            start = int(match.group(1))
            destination = int(match.group(2))
            # run loop for dijkstra
            distances, path = dijkstra_loop(adj, start, destination)
            # append results to their lists
            results.append((start, destination, distances[destination]))
            paths.append(path)
    # reformat lists for output
    for i in range(len(results)):
        path_nodes = paths[i]
        formatted_results.append([])
        for j, node in enumerate(path_nodes):
            if j < len(path_nodes) - 1:
                formatted_results[i].append("City" + str(node) + "->")
            else:
                formatted_results[i].append("City" + str(node))   

    return results, formatted_results

def dijkstra_loop(adj, start, destination):
    # set paths and distance array to infinity and zero for all spaces
    distances = {node: float('inf') for node in adj}
    previous_nodes = {node: None for node in adj}
    # zero starting distance
    distances[start] = 0
    priority_queue = [(0, start)]
    visited = set()

    while priority_queue:
        # choose the smallest distance
        current_distance, current_node = heapq.heappop(priority_queue)
        # avoid cycles
        if  current_node in visited:
            continue
        visited.add(current_node)
        # check if longer distance, if shotest path found already, continue
        if current_distance > distances[current_node]:
            continue
        # check neighbor nodes
        for neighbor, weight in adj[current_node].items():
            distance = current_distance + weight
            # if distance is less update neighbor
            if distance < distances[neighbor]:
                previous_nodes[neighbor] = current_node
                distances[neighbor] = distance
                # push to priority queue
                heapq.heappush(priority_queue, (distance, neighbor))
    # path traces previous nodes
    path = []
    path_node = destination
    while path_node is not None:
        path.append(path_node)
        path_node = previous_nodes[path_node]
    path.reverse() # place path into correct direction
    return distances, path

# output loop for dijkstra
def formatted_dijkstra_output(distances, paths):
    for i in range(len(distances)):
                    print("SHORTEST_PATH CITY" + str(distances[i][0]) + " City" + str(distances[i][1]) + ":", end="")
                    for node in  paths[i]:
                        print(" " + node, end="")
                    print(" (cost: " + str(distances[i][2]) + ")")


# Guard executable lines from running when imported into another script
if __name__ == "__main__":
    fileinput = sys.argv[1]
    fileinput2 = sys.argv[2]
    try:
        with open(fileinput, 'r') as file:
            with open(fileinput2, 'r') as file2:
                weighted_array, edge_list = build_graph(fileinput)
                weighted_array = update_traffic(file2)
                file2.seek(0)
                adj = edge_list_to_adjacency_list(edge_list)
                distances, paths = dijkstra(adj, file2)
    
                formatted_dijkstra_output(distances, paths)
                
    except FileNotFoundError:
        print(f"Error: The file '{fileinput}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")