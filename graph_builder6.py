import re
import sys

# Global adjacency matrix initialization
weighted_array = []

def add_node():
    # Iterate through rows to add column for city
    for row in weighted_array:
        row.append(0)
    # Create a row with no edges
    new_row = [0 for i in range(len(weighted_array) + 1)]
    weighted_array.append(new_row)


def add_edge(start, destination, weight):
    # Overwrite weight of an edge from start to destination
    weighted_array[start][destination] = weight


def remove_node(node):
    # Zero any row / edge going to or from the node
    for rows in weighted_array:
        if rows[node] != 0:
            rows[node] = 0
    # Remove the row from the node
    weighted_array.pop(node)
    
    
def remove_edge(start, destination):
    # Zero out weight of an edge from start to destination
    weighted_array[start][destination] = 0


def to_adjacency_list():
    # Print formatted list from weighted_array
    i, j = 0 , 0
    fin = [("City"+str(i)+":") for i in range(len(weighted_array))] # Formatting
    first = True
    for rows in weighted_array:
        j = 0  
        for cols in rows:
            if cols != 0:
                if first == True:
                    fin[i] += " City" + str(j) + "(" + str(cols) + ")" # Formatting
                    first = False
                else:
                    fin[i] += ", City" + str(j) + "(" + str(cols) + ")" # Formatting
            j += 1
        first = True
        i += 1
    for routes in fin:
        print(routes)

# Make graph building logic a defined function for reuse
def build_graph(file_path):
    # Parses input file with cities and roads and returns adjacency list and edge list
    pattern1 = re.compile(r"City(\d+) City(\d+) (\d+)")

    number_of_cities = 0
    number_of_roads = 0
    city_counter_mode = False
    road_counter_mode = False
    with open(file_path, 'r') as file:
        # First pass counts cities and roads
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

        # Prepare adjacency matrix from cities
        weighted_array = [[0 for _ in range(number_of_cities)] for _ in range(number_of_cities)]
        edge_list = []

        # Second pass parses edges
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
    return weighted_array, edge_list # Return weighted array with edge list for reuse

# Guard executable lines from running when imported into another script
if __name__ == "__main__":
    # python3 graph_builder6.py input1.txt <- sets listed argument
    fileinput = sys.argv[1]
    # Build graph from input
    weighted_array, edge_list = build_graph(fileinput)
    # Print formatted list
    to_adjacency_list()
