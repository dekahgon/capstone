import pandas as pd
import networkx as nx
import folium

# =========================================================
# 1. LOAD DATA
# =========================================================
stops     = pd.read_csv('ny_data/stops.txt') # stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station
stop_times = pd.read_csv('ny_data/stop_times.txt') # trip_id,arrival_time,departure_time,stop_id,stop_sequence
trips     = pd.read_csv('ny_data/trips.txt') # trip_id,route_id,service_id,trip_headsign,trip_short_name
routes    = pd.read_csv('ny_data/routes.txt') # route_id,route_short_name,route_long_name,route_type

# =========================================================
# 2. CLEAN STOP IDs
# Merge directional platform variants (101N / 101S → 101)
# so each physical station is one node, not two
# =========================================================
def normalize_stop_id(stop_id):
    s = str(stop_id)
    return s[:-1] if s[-1] in ('N', 'S') else s

stop_times['stop_id'] = stop_times['stop_id'].apply(normalize_stop_id)
stops['stop_id'] = stops['stop_id'].apply(normalize_stop_id)
stops = stops.drop_duplicates(subset='stop_id')

# =========================================================
# 3. BUILD GRAPH
# =========================================================
G = nx.Graph() # Initialize empty graph

for _, row in stops.iterrows(): # Add the nodes (stations) to the graph
    G.add_node(row['stop_id'],
               name=row['stop_name'],
               lat=row['stop_lat'],
               lon=row['stop_lon'])

# Add the edges (connections) to the graph
stop_times_sorted = stop_times.sort_values(['trip_id', 'stop_sequence'])
for _, group in stop_times_sorted.groupby('trip_id'):
    stop_ids = group['stop_id'].tolist()
    for i in range(len(stop_ids) - 1):
        G.add_edge(stop_ids[i], stop_ids[i + 1])

# =========================================================
# 4. SEPARATE THE THREE NETWORKS
# Raw GTFS contains orphan stops and small disconnected
# shuttles — keep only the largest connected component
# =========================================================
components  = sorted(nx.connected_components(G), key=len, reverse=True)
# Main metro network = largest connected component

# Manhattan train network

# Staten Island train network
main_component = components[0]
trains   = set(G.nodes()) - main_component

G_main      = G.subgraph(main_component).copy()
n_discarded = len(trains)


# =========================================================
# 5. NETWORK METRICS
# =========================================================
degree_dict  = dict(G_main.degree())
top_stations = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:10]
top_named    = [(G_main.nodes[sid].get('name', sid), deg) for sid, deg in top_stations]

betweenness  = nx.betweenness_centrality(G_main)
top_between  = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
top_between_named = [(G_main.nodes[sid].get('name', sid), round(val, 4))
                     for sid, val in top_between]

avg_path     = nx.average_shortest_path_length(G_main)
fiedler      = nx.algebraic_connectivity(G_main)

# =========================================================
# 6. PRINT SUMMARY
# =========================================================
print("=" * 55)
print("  NYC SUBWAY — NETWORK SUMMARY")
print("=" * 55)

print(f"\n  Stations (nodes):       {G_main.number_of_nodes()}")
print(f"  Connections (edges):    {G_main.number_of_edges()}")
print(f"  Orphan stops removed:   {n_discarded}")

print(f"\n  Avg. shortest path:     {avg_path:.4f} stops")
print(f"  Algebraic connectivity: {fiedler:.6f}")

print("\n  Top 10 — Most connected stations (degree):")
for i, (name, deg) in enumerate(top_named, 1):
    print(f"    {i:>2}. {name:<40} {deg} connections")

print("\n  Top 10 — Biggest bottlenecks (betweenness centrality):")
for i, (name, val) in enumerate(top_between_named, 1):
    print(f"    {i:>2}. {name:<40} {val}")

print("=" * 55)

# =========================================================
# 7. INTERACTIVE MAP
# Color coding:
#   Main network edges  → blue (#3a86ff)
#   Main network nodes  → pink/red (#ff006e)
#   Orphan edges        → bright cyan (#00f5ff)
#   Orphan nodes        → bright cyan (#00f5ff), larger radius
# =========================================================
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
 
# --- Draw edges ---
for u, v in G.edges():
    n1, n2 = G.nodes[u], G.nodes[v]
    if not (n1.get('lat') and n2.get('lat')):
        continue
 
    is_orphan_edge = (u in orphan_nodes) or (v in orphan_nodes)
 
    folium.PolyLine(
        [(n1['lat'], n1['lon']), (n2['lat'], n2['lon'])],
        color="#dc2e2e" if is_orphan_edge else '#3a86ff',
        weight=2,
        opacity= 0.7
    ).add_to(m)
 
# --- Draw nodes ---
for node, data in G.nodes(data=True):
    if not data.get('lat'):
        continue
 
    is_orphan = node in orphan_nodes
 
    folium.CircleMarker(
        location=[data['lat'], data['lon']],
        radius= 4,
        color="#3ddde2" if is_orphan else '#ff006e',
        fill=True,
        fill_color="#3ddde2" if is_orphan else '#ff006e',
        fill_opacity=0.9,
        popup=folium.Popup(
            f"{'⚠ ORPHAN: ' if is_orphan else ''}{data.get('name', node)}",
            max_width=200
        )
    ).add_to(m)
 
m.save('nyc_subway.html')
print("\n  Map saved → nyc_subway.html")
print("  (bright cyan = disconnected/orphan stops)")
print("=" * 55)