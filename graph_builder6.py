import re
import sys

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
    try:
        with open(file_path, 'r') as file:
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

            file.seek(0)

            road_mode = False

            for line in file:
                clean_line = line.strip()
                match = pattern1.search(clean_line)
                if match:
                    start = int(match.group(1))
                    destination = int(match.group(2))
                    weight = int(match.group(3))
                    weighted_array[start][destination] = weight

            return weighted_array # Add return for reusing populated weighted array elsewhere
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def update_traffic(file_path):
    traffic_pattern = re.compile(r"TRAFFIC_REPORT City(\d+) City(\d+) ([-+]?\d+)")
    try:
        with open(file_path, 'r') as file:
            for line in file:
                clean_line = line.strip()
                match = traffic_pattern.search(clean_line)
                if match:
                    start = int(match.group(1))
                    destination = int(match.group(2))
                    traffic = int(match.group(3))
                    weighted_array[start][destination] += traffic
            return weighted_array
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")



# Guard executable lines from running when imported into another script
if __name__ == "__main__":
    fileinput = sys.argv[1]
    weighted_array = build_graph(fileinput)
    to_adjacency_list()
    
    file2 = sys.argv[2]
    weighted_array = update_traffic(file2)

    to_adjacency_list()
