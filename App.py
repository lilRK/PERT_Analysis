from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from networkx.drawing.nx_pydot import graphviz_layout

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

class Activity:
    def __init__(self, name, duration, precedents):
        self.name = name
        self.duration = duration
        self.precedents = precedents

def create_graph(activities):
    G = nx.DiGraph()
    G.add_node('Start', duration=0)
    G.add_node('End', duration=0)
   
    for activity in activities:
        G.add_node(activity.name, duration=activity.duration)
        if not activity.precedents:
            G.add_edge('Start', activity.name)
        for precedent in activity.precedents:
            G.add_edge(precedent, activity.name)
   
    for node in G.nodes():
        if G.out_degree(node) == 0 and node != 'End':
            G.add_edge(node, 'End')
   
    return G

def forward_pass(G):
    earliest_start = {node: 0 for node in G.nodes()}
    for node in nx.topological_sort(G):
        for successor in G.successors(node):
            earliest_start[successor] = max(earliest_start[successor], earliest_start[node] + G.nodes[node]['duration'])
    return earliest_start

def backward_pass(G, earliest_finish):
    latest_finish = {node: earliest_finish[max(earliest_finish, key=earliest_finish.get)] for node in G.nodes()}
    for node in reversed(list(nx.topological_sort(G))):
        for predecessor in G.predecessors(node):
            latest_finish[predecessor] = min(latest_finish[predecessor], latest_finish[node] - G.nodes[node]['duration'])
    return latest_finish

def find_critical_path(G, earliest_start, latest_finish):
    critical_path = []
    current_node = 'Start'
    while current_node != 'End':
        critical_path.append(current_node)
        for successor in G.successors(current_node):
            if earliest_start[successor] == latest_finish[successor] - G.nodes[successor]['duration']:
                current_node = successor
                break
    critical_path.append('End')
    return critical_path

def plot_graph(G, earliest_start, latest_finish, critical_path):
    images = {}

    # Forward Pass Graph
    plt.figure(figsize=(12, 8))
    pos = graphviz_layout(G, prog='dot')
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10, font_color='black', arrows=True, node_shape='o', width=2)
    edge_labels = {(u, v): f"{G.nodes[u]['duration']}" for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    for node, es in earliest_start.items():
        x, y = pos[node]
        plt.text(x, y + 10, s=f"ES: {es}", bbox=dict(facecolor='white', alpha=0.7), horizontalalignment='center', fontsize=9, verticalalignment='bottom')
    plt.title('Forward Pass')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    images['forwardPassGraph'] = base64.b64encode(img.getvalue()).decode()

    # Backward Pass Graph
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', node_size=2000, font_size=10, font_color='black', arrows=True, node_shape='o', width=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    for node, lf in latest_finish.items():
        x, y = pos[node]
        plt.text(x, y - 10, s=f"LF: {lf}", bbox=dict(facecolor='white', alpha=0.7), horizontalalignment='center', fontsize=9, verticalalignment='top')
    plt.title('Backward Pass')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    images['backwardPassGraph'] = base64.b64encode(img.getvalue()).decode()

    # Critical Path Graph
    plt.figure(figsize=(12, 8))
    color_map = ['red' if node in critical_path else 'lightgrey' for node in G.nodes()]
    edge_colors = ['red' if (u in critical_path and v in critical_path) else 'black' for u, v in G.edges()]
    nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=2000, font_size=10, font_color='black', arrows=True, node_shape='o', width=2, edge_color=edge_colors)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title('Critical Path')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    images['criticalPathGraph'] = base64.b64encode(img.getvalue()).decode()

    return images


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    activities_data = data['activities']

    # Convert activities_data to Activity objects
    activities = [
        Activity(
            name=activity['name'],
            duration=(float(activity['optimisticTime']) + 4 * float(activity['mostLikelyTime']) + float(activity['pessimisticTime'])) / 6,  # PERT formula
            precedents=activity['precedents'].split(',') if activity['precedents'] else []
        )
        for activity in activities_data
    ]

    G = create_graph(activities)
    earliest_start = forward_pass(G)
    latest_finish = backward_pass(G, earliest_start)
    critical_path = find_critical_path(G, earliest_start, latest_finish)

    estimated_duration = sum(G.nodes[node]['duration'] for node in critical_path)
    
    images = plot_graph(G, earliest_start, latest_finish, critical_path)
    
    return jsonify({
        'forwardPassGraph': images['forwardPassGraph'],
        'backwardPassGraph': images['backwardPassGraph'],
        'criticalPathGraph': images['criticalPathGraph'],
        'estimatedDuration': estimated_duration  # Assuming cost is same as duration for simplicity
    })


if __name__ == '__main__':
    app.run(debug=True)