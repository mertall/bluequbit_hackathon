import sys
import networkx as nx
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit

def load_qasm_file(file_path):
    """
    Loads a QASM file and returns a QuantumCircuit object.
    """
    try:
        with open(file_path, 'r') as file:
            qasm_str = file.read()
        qc = QuantumCircuit.from_qasm_str(qasm_str)
        return qc
    except Exception as e:
        print(f"Error loading QASM file: {e}")
        sys.exit(1)

def extract_cz_connections(qc):
    """
    Extracts all CZ gate connections from the QuantumCircuit.
    
    Returns:
        A list of tuples representing edges between qubits.
    """
    cz_edges = []
    for instruction, qargs, cargs in qc.data:
        if instruction.name == 'cz':
            # Qubit indices
            qubit1 = qc.find_bit(qargs[0]).index
            qubit2 = qc.find_bit(qargs[1]).index
            # Ensure smaller index comes first for consistency
            edge = tuple(sorted((qubit1, qubit2)))
            cz_edges.append(edge)
    return cz_edges

def create_connectivity_graph(cz_edges, total_qubits):
    """
    Creates a NetworkX graph from CZ gate connections.
    
    Args:
        cz_edges: List of tuples representing CZ connections.
        total_qubits: Total number of qubits in the circuit.
        
    Returns:
        A NetworkX graph object.
    """
    G = nx.Graph()
    # Add all qubits as nodes
    G.add_nodes_from(range(total_qubits))
    # Add CZ connections as edges
    G.add_edges_from(cz_edges)
    return G

def plot_connectivity_graph(G, title='Qubit Connectivity Graph Based on CZ Gates'):
    """
    Plots the connectivity graph using Matplotlib.
    
    Args:
        G: NetworkX graph object.
        title: Title of the plot.
    """
    plt.figure(figsize=(12, 12))
    
    # Choose a layout for better visualization
    pos = nx.spring_layout(G, seed=42)  # Positions for all nodes
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=300, node_color='lightblue')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7)
    
    # Draw labels
    labels = {qubit: f'q[{qubit}]' for qubit in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10)
    
    plt.title(title)
    plt.axis('off')
    plt.show()

def prune_graph_knn(G, k=35):
    """
    Prunes the graph to retain only the top 'k' qubits based on degree centrality.
    
    Args:
        G: Original NetworkX graph.
        k: Number of qubits to retain.
        
    Returns:
        pruned_qubits: List of qubit indices that are pruned (removed).
        pruned_graph: NetworkX graph after pruning.
    """
    if k >= G.number_of_nodes():
        print(f"The graph has {G.number_of_nodes()} qubits, which is less than or equal to the desired {k} qubits.")
        return [], G.copy()
    
    # Compute degree for each qubit
    degrees = G.degree()
    # Sort qubits based on degree in descending order
    sorted_qubits = sorted(degrees, key=lambda x: x[1], reverse=True)
    print(sorted_qubits)
    
    # Select top 'k' qubits to retain
    retained_qubits = set([qubit for qubit, degree in sorted_qubits[:k]])
    # Identify qubits to prune
    pruned_qubits = set(G.nodes()) - retained_qubits
    
    # Create a pruned graph
    pruned_graph = G.subgraph(retained_qubits).copy()
    
    return list(pruned_qubits), pruned_graph

def main():
    # Path to your QASM file
    qasm_file = "./circuit_2_42q.qasm"
    
    # Load the QASM file
    qc = load_qasm_file(qasm_file)
    
    # Extract CZ gate connections
    cz_edges = extract_cz_connections(qc)
    
    # Total number of qubits
    total_qubits = qc.num_qubits
    print(f"Total number of qubits: {total_qubits}")
    
    # Create the original connectivity graph
    G_original = create_connectivity_graph(cz_edges, total_qubits)
    
    # Plot the original connectivity graph
    plot_connectivity_graph(G_original, title='Original Qubit Connectivity Graph (All Qubits)')
    
    # Apply KNN-Based Pruning to retain only 35 qubits
    desired_qubits = 34
    pruned_qubits, G_pruned = prune_graph_knn(G_original, k=desired_qubits)
    
    print(f"Number of qubits to prune: {len(pruned_qubits)}")
    print(f"Pruned qubits (removed): {pruned_qubits}")
    
    # Plot the pruned connectivity graph
    plot_connectivity_graph(G_pruned, title=f'Pruned Qubit Connectivity Graph (Top {desired_qubits} Qubits)')
    
    # Optionally, save the pruned graph or perform further analysis
    # For example, saving the pruned graph to a file:
    # nx.write_gml(G_pruned, "pruned_connectivity_graph.gml")

if __name__ == "__main__":
    main()
