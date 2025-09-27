import sys
import re
import os
import graph_builder6 as bg
import graph_query6 as gq

# lists that keep scheduled deliveries, history, and action log for undo
scheduled = [] # (src, dst, time_str, time_min)
history = [] # (src, dst, time_str, time_min, route, cost)
action_log = [] # (action_type, data)

# Format "HH:MM" time string to total minutes for easy comparison
def time_to_min(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

# Schedule a delivery
def schedule_delivery(src, dst, t_str):
    t_min = time_to_min(t_str) # convert to minutes for easy sorting
    entry = (src, dst, t_str, t_min) # tuple for easy unpacking
    scheduled.append(entry)
    action_log.append(('schedule', entry))
    print(f"Scheduled: City{src}->City{dst} at {t_str}")

# Record history of scheduled deliveries, compute routes if possible
def record_history():
    if not scheduled:
        print("No scheduled deliveries to record")
        return

    input1_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input1.txt") # path to input1.txt
    if not os.path.exists(input1_path): # if input1.txt missing
        print(f"Warning: '{input1_path}' not found. Routes will not be computed.")
        adj = None # no graph available
    else:
        graph_data = bg.build_graph(input1_path) # returns (weighted_array, edge_list) from builder
        edge_list = graph_data[1]  # take just the edge list
        adj = gq.edge_list_to_adjacency_list(edge_list) # converts to adjacency list

    batch = list(scheduled)
    scheduled.clear()
    batch_ext = []

    for src, dst, t_str, t_min in batch:
        route = None
        cost = None
        if adj and src in adj: # only if graph exists and src is valid
            try: 
                dist, parent = gq.dijkstra_loop(adj, src, return_parent=True) # run dijkstra
                d = dist.get(dst, float('inf')) # get distance to dst
                if d != float('inf'): # if reachable
                    route = gq.reconstruct_path(parent, src, dst) # reconstruct path
                    cost = int(d) # set cost
            except:
                pass
        ext = (src, dst, t_str, t_min, route, cost)
        history.append(ext)
        batch_ext.append(ext)

    action_log.append(('record', batch_ext))
    print("Recorded history")

# Undo the last scheduled or recorded action
def undo_last():
    for i in range(len(action_log)-1, -1, -1):
        act, entry = action_log[i] # unpack action log into type and data
        if act == 'schedule':
            action_log.pop(i) # remove from log
            try: 
                scheduled.remove(entry) # remove from scheduled
                print("Undid last action") 
                return 
            except Exception: 
                pass
            # try remove from history
            for j in range(len(history)-1, -1, -1):
                h_src, h_dst, _, h_min, _, _ = history[j]  # inline unpacking
                if h_src == entry[0] and h_dst == entry[1] and h_min == entry[3]: # histroy matches entry from action log
                    history.pop(j)
                    print("Undid last action from history")
                    return
            print("Could not find action to undo")
            return
    print("Nothing to undo")

# Query history between two times, inclusive
def query_history(start_s, end_s): 
    start_t = time_to_min(start_s)
    end_t = time_to_min(end_s)
    results = [e for e in history if start_t <= e[3] <= end_t] # filter by time range

    print(f"History between {start_s} and {end_s}:")
    if not results:
        print("- (no records)")
        return

    for src, dst, t_str, _, route, cost in results:
        if not route:
            print(f"- City{src}->City{dst} at {t_str} (route: unreachable)")
        else:
            path = " -> ".join(f"City{n}" for n in route)
            if cost is None:
                print(f"- {path} at {t_str}")
            else:
                print(f"- {path} (cost: {cost}) at {t_str}")


if __name__ == "__main__":
    file_path = sys.argv[1] # schedule3.txt

    schedule_pattern = re.compile(r"^SCHEDULE DELIVERY\s+City(\d+)->City(\d+)\s+at\s+([0-9:]+)$") 
    record_pattern = re.compile(r"^RECORD_HISTORY$")
    undo_pattern = re.compile(r"^UNDO_LAST$")
    query_pattern = re.compile(r"^QUERY_HISTORY BETWEEN\s+([0-9:]+)\s+([0-9:]+)$")

    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                match = schedule_pattern.search(line)
                if match:
                    src = int(match.group(1))
                    dst = int(match.group(2))
                    t = match.group(3)
                    schedule_delivery(src, dst, t)
                    continue

                if record_pattern.search(line):
                    record_history()
                    continue

                if undo_pattern.search(line):
                    undo_last()
                    continue

                match = query_pattern.search(line)
                if match:
                    start = match.group(1)
                    end = match.group(2)
                    query_history(start, end)
                    continue

                print(f"Unrecognized command: {line}")
    except FileNotFoundError:
        print(f"Error: file not found: {file_path}")
        sys.exit(2)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(3)