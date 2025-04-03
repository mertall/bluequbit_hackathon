import sys
import networkx as nx
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram

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

def find_most_connected_qubit(G):
    """
    Identifies the qubit with the highest number of connections.
    
    Args:
        G: NetworkX graph object.
        
    Returns:
        The qubit index with the most connections and its degree.
    """
    degrees = G.degree()
    # Find the qubit with the maximum degree
    most_connected = max(degrees, key=lambda x: x[1])
    qubit_index, degree = most_connected
    print(f"\nQubit with the most connections: q[{qubit_index}] with {degree} connections.")
    return qubit_index

def determine_qubit_bitstring(qubit_index, measurement_counts):
    """
    Determines the state of a specific qubit from measurement counts.
    
    Args:
        qubit_index (int): The index of the qubit to analyze.
        measurement_counts (dict): A dictionary of measurement results (bitstrings and their counts).
        
    Returns:
        A dictionary with the state ('0' or '1') and their respective counts for the qubit.
    """
    qubit_state_counts = {'0': 0, '1': 0}
    
    for bitstring, count in measurement_counts.items():
        # Assuming q[0] is the least significant bit
        # Reverse the bitstring to align indices (q[0] = bitstring[-1])
        reversed_bitstring = bitstring[::-1]
        if qubit_index < len(reversed_bitstring):
            qubit_state = reversed_bitstring[qubit_index]
            if qubit_state in qubit_state_counts:
                qubit_state_counts[qubit_state] += count
            else:
                qubit_state_counts[qubit_state] = count
        else:
            print(f"Warning: Qubit index {qubit_index} exceeds bitstring length.")
    
    print(f"\nState distribution for q[{qubit_index}]:")
    for state, cnt in qubit_state_counts.items():
        print(f"State {state}: {cnt} counts")
    
    return qubit_state_counts

def plot_qubit_state_distribution(qubit_state_counts, qubit_index):
    """
    Plots the state distribution of a specific qubit.
    
    Args:
        qubit_state_counts (dict): Dictionary with states and their counts.
        qubit_index (int): The index of the qubit.
    """
    states = list(qubit_state_counts.keys())
    counts = list(qubit_state_counts.values())
    
    plt.figure(figsize=(6, 4))
    plt.bar(states, counts, color=['skyblue', 'salmon'])
    plt.xlabel('State')
    plt.ylabel('Counts')
    plt.title(f'State Distribution for q[{qubit_index}]')
    plt.show()

def main():
    qasm_file = "./circuit_3_60q.qasm"
    
    # Load the QASM file
    qc = load_qasm_file(qasm_file)
    
    # Extract CZ gate connections
    cz_edges = extract_cz_connections(qc)
    
    # Total number of qubits
    total_qubits = qc.num_qubits
    
    # Create the connectivity graph
    G = create_connectivity_graph(cz_edges, total_qubits)
    
    # Plot the graph
    plot_connectivity_graph(G)
    
    # Identify the qubit with the most connections
    most_connected_qubit = find_most_connected_qubit(G)
    
    # Placeholder for measurement counts
    # Replace this dictionary with your actual measurement counts
    # Example:
    # measurement_counts = {'000...0': 1000, '000...1': 500, ...}
    measurement_counts = {}  # TODO: Populate this with actual data
    
    if measurement_counts:
        # Determine the state distribution for the most connected qubit
        qubit_state_counts = determine_qubit_bitstring(most_connected_qubit, measurement_counts)
        
        # Plot the state distribution
        plot_qubit_state_distribution(qubit_state_counts, most_connected_qubit)
    else:
        print("\nNo measurement counts available to determine qubit states.")
        print("Please provide measurement counts to analyze qubit states.")

if __name__ == "__main__":
    main()
