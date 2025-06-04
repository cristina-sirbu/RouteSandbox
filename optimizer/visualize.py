import json
import networkx as nx
import matplotlib.pyplot as plt

# Load sample optimizer output
with open("optimizer/sample_output.json") as f:
    result = json.load(f)

# Optional: print for inspection
print("Loaded routes:", json.dumps(result, indent=2))

# Create a directed graph
G = nx.DiGraph()

# Add nodes and edges
for route in result["routes"]:
    stops = route["stops"]
    vehicle = route["vehicle_id"]
    for i in range(len(stops) - 1):
        from_id = stops[i]["location_id"]
        to_id = stops[i + 1]["location_id"]
        G.add_edge(from_id, to_id, label=f"V{vehicle}")

# Layout and draw
pos = nx.spring_layout(G, seed=42)  # consistent layout

nx.draw(G, pos, with_labels=True, node_color="lightblue", arrows=True)
edge_labels = nx.get_edge_attributes(G, "label")
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

plt.title("Optimized Delivery Routes")
plt.show()
