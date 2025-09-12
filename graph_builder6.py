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


def update_traffic(file):
    traffic_pattern = re.compile(r"TRAFFIC_REPORT City(\d+) City(\d+) ([-+]?\d+)")

    for line in file:
        clean_line = line.strip()
        match = traffic_pattern.search(clean_line)
        if match:
            start = int(match.group(1))
            destination = int(match.group(2))
            traffic = int(match.group(3))
            weighted_array[start][destination] += traffic
    return weighted_array

def edge_list_to_adjacency_list(edge_list):
    adj_list = {}
    for(src, dest, weight) in edge_list:
        if src not in adj_list:
            adj_list[src] = {}


        adj_list[src][dest] = weight
 
    return adj_list

def dijkstra(adj, file):
    traffic_pattern = re.compile(r"QUERY SHORTEST_PATH City(\d+) City(\d+)")
    results = []
    for line in file:
        clean_line = line.strip()
        match = traffic_pattern.search(clean_line)
        if match:

            start = int(match.group(1))
            destination = int(match.group(2))

            distances = dijkstra_loop(adj, start)

            results.append((start, destination, distances[destination]))
    return results
    
def dijkstra_loop(adj, start):
    distances = {node: float('inf') for node in adj}
    distances[start] = 0
    priority_queue = [(0, start)]
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        if current_distance > distances[current_node]:
            continue
        for neighbor, weight in adj[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
    return distances



# Guard executable lines from running when imported into another script
if __name__ == "__main__":
    fileinput = sys.argv[1]
    fileinput2 = sys.argv[2]
    try:
        with open(fileinput, 'r') as file:
            with open(fileinput2, 'r') as file2:

                weighted_array, edge_list = build_graph(fileinput)
                adj = edge_list_to_adjacency_list(edge_list)
                distances = dijkstra(adj, file2)

                print(distances)

                
    except FileNotFoundError:
        print(f"Error: The file '{fileinput}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")