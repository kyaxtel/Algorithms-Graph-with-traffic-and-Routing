import sys
import heapq
import re
import graph_builder6 as bg

# Apply traffic reports to adjust edge weights with a min of 1
def update_traffic(adj, file):
    traffic_pattern = re.compile(r"TRAFFIC_REPORT City(\d+) City(\d+) ([-+]?\d+)")

    for line in file:
        clean_line = line.strip()
        match = traffic_pattern.search(clean_line)
        if match:
            start = int(match.group(1))
            destination = int(match.group(2))
            traffic = int(match.group(3))
            # If edge exists update weight clamped to 1
            if start in adj and destination in adj[start]:
                adj[start][destination] = max(1, adj[start][destination] + traffic)
    return adj

# Convert edge list to adjacency list
def edge_list_to_adjacency_list(edge_list):
    adj_list = {}
    for(src, dest, weight) in edge_list:
        if src not in adj_list:
            adj_list[src] = {}
        adj_list[src][dest] = weight
        # Make sure all cities have a key
        adj_list.setdefault(dest, {})
    return adj_list

# Reconstruct path from parent dict by walking through then reversing
def reconstruct_path(parent, start, destination):
    path = []
    current = destination
    while current is not None:
        path.append(current)
        # Stop when at start (No parent)
        if current == start and parent[current] is None:
            break
        current = parent[current]
    path.reverse()
    return path

# Remove edges of a visited path for iterative Dijkstra kpaths
def remove_path_edges(adj, path):
    new_adj = {city: neighbors.copy() for city, neighbors in adj.items()}
    for i in range(len(path) - 1):
        current_city = path[i]
        next_city = path[i + 1]
        if next_city in new_adj.get(current_city, {}):
            del new_adj[current_city][next_city]
    return new_adj

# Controller for dijkstra, runs dijkstra and returns best path if available
def dijkstra(adj, file):
    traffic_pattern = re.compile(r"QUERY SHORTEST_PATH City(\d+) City(\d+)")
    results = []
    for line in file:
        clean_line = line.strip()
        match = traffic_pattern.search(clean_line)
        if match:
            start = int(match.group(1))
            destination = int(match.group(2))

            # Run dijkstra and request parents for reconstruction
            distances, parent = dijkstra_loop(adj, start, return_parent=True)
            d = distances.get(destination, float('inf'))

            # No route found
            if d == float('inf'):
                results.append(f"SHORTEST_PATH City{start} City{destination}: unreachable")
                continue
            # Rebuild and format
            path = reconstruct_path(parent, start, destination)
            path_string = " -> ".join(f"City{n}" for n in path)
            results.append(f"SHORTEST_PATH City{start} City{destination}: {path_string} (cost: {int(d)})")
    return results

# Base dijkstra loop with priority queue, returns distances and parents if requested
def dijkstra_loop(adj, start, return_parent=False):
    distances = {node: float('inf') for node in adj}
    parent = {node: None for node in adj} if return_parent else None
    distances[start] = 0
    priority_queue = [(0, start)]
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        # If a better route has already been found then skip
        if current_distance > distances[current_node]:
            continue
        # Check each outgoing node and update distance + parent if current node gives better path
        for neighbor, weight in adj[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                if parent is not None:
                    parent[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))
    return (distances, parent) if return_parent else distances

# Controller for k paths, runs dijkstra then removes edges and reruns for all paths
def k_paths(adj, file):
    kpaths_pattern = re.compile(r"QUERY K_PATHS City(\d+) City(\d+) (\d+)")
    results = []
    for line in file:
        clean_line = line.strip()
        match = kpaths_pattern.search(clean_line)
        if match:
            start = int(match.group(1))
            destination = int(match.group(2))
            k = int(match.group(3))

            # Calculate k distinct paths
            paths = k_paths_loop(adj, start, destination, k)
            # No alternate path
            if not paths:
                results.append(f"K_PATHS City{start} City{destination} {k}: unreachable")
                continue
            # Format results
            results.append(f"K_PATHS City{start} City{destination}:")
            for iteration, (path_nodes, distance) in enumerate(paths, 1):
                path_string = " -> ".join(f"City{n}" for n in path_nodes)
                results.append(f" {iteration}) {path_string} (cost: {distance})")
    return results

# Base k paths loop, returns k paths by removing visited edges
def k_paths_loop(adj, start, destination, k):
    paths = []
    adj_copy = {city: neighbors.copy() for city, neighbors in adj.items()}
    for iteration in range(k):
        distances, parent = dijkstra_loop(adj_copy, start, return_parent=True)
        d = distances.get(destination, float('inf'))
        # If out of paths stop
        if d == float('inf'):
            break
        path = reconstruct_path(parent, start, destination)
        if not path:
            break
        paths.append((path, int(d)))
        # Remove edges of visited path before starting process again
        adj_copy = remove_path_edges(adj_copy, path)
    return paths

# Guard executable lines from running when imported into another script
if __name__ == "__main__":
    fileinput = sys.argv[1] # input1.txt
    fileinput2 = sys.argv[2] # commands2.txt
    try:
        # Use module 1 import to build graph
        weighted_array, edge_list = bg.build_graph(fileinput) # builds adjacency matrix
        adj = edge_list_to_adjacency_list(edge_list) # converts to adjacency list
        with open(fileinput2, 'r') as file2:
                # First apply traffic reports
                adj = update_traffic(adj, file2)
                # Second find shortest path with dijkstra
                file2.seek(0)
                distances = dijkstra(adj, file2)
                # Third find k paths with iterative dijkstra
                file2.seek(0)
                kpaths = k_paths(adj, file2)
                # Print results
                print("\n".join(distances))
                print("\n".join(kpaths))

    except FileNotFoundError:
        print(f"Error: The file '{fileinput}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
