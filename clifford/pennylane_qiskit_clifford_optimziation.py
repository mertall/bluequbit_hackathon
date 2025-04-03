# import sys
# import numpy as np
# from collections import Counter

# # Qiskit Imports
# from qiskit import QuantumCircuit
# from qiskit_aer import AerSimulator

# # PennyLane Imports
# import pennylane as qml
# from pennylane import clifford_t_decomposition

# def load_qasm(file_path):
#     """
#     Loads a QASM file into a Qiskit QuantumCircuit.

#     Args:
#         file_path (str): Path to the QASM file.

#     Returns:
#         QuantumCircuit: The loaded quantum circuit.
#     """
#     try:
#         qc = QuantumCircuit.from_qasm_file(file_path)
#         print("QASM file loaded successfully.\n")
#         return qc
#     except Exception as e:
#         print(f"Error loading QASM file: {e}")
#         sys.exit(1)

# def convert_qiskit_to_pennylane(qc):
#     """
#     Converts a Qiskit QuantumCircuit to a PennyLane QuantumTape.

#     Args:
#         qc (QuantumCircuit): The Qiskit quantum circuit.

#     Returns:
#         pennylane.tape.QuantumTape: The converted PennyLane circuit.
#     """
#     try:
#         pl_circuit = qml.from_qiskit(qc)
#         print("Conversion from Qiskit to PennyLane successful.\n")
#         return pl_circuit
#     except Exception as e:
#         print(f"Error converting to PennyLane circuit: {e}")
#         sys.exit(1)

# def apply_clifford_t_decomposition(pl_circuit):
#     """
#     Applies Clifford-T decomposition to a PennyLane circuit.

#     Args:
#         pl_circuit (pennylane.tape.QuantumTape): The PennyLane circuit.

#     Returns:
#         pennylane.tape.QuantumTape: The decomposed PennyLane circuit.
#     """
#     try:
#         decomposed_circuit = clifford_t_decomposition(pl_circuit)
#         print("Clifford-T decomposition applied successfully.\n")
#         return decomposed_circuit
#     except Exception as e:
#         print(f"Error during Clifford-T decomposition: {e}")
#         sys.exit(1)

# def simulate_with_pennylane(decomposed_circuit, shots=100):
#     """
#     Simulates the decomposed PennyLane circuit using PennyLane's simulator.

#     Args:
#         decomposed_circuit (pennylane.tape.QuantumTape): The decomposed PennyLane circuit.
#         shots (int): Number of simulation shots.

#     Returns:
#         dict: Measurement counts.
#     """
#     try:
#         # Verify the type of decomposed_circuit
#         print(f"Type of decomposed_circuit: {type(decomposed_circuit)}")
#         if not isinstance(decomposed_circuit, qml.tape.QuantumTape):
#             raise TypeError("decomposed_circuit is not a QuantumTape.")

#         num_wires = decomposed_circuit.num_wires

#         # Define a PennyLane device that supports non-Clifford gates
#         dev = qml.device("default.qubit", wires=num_wires, shots=shots)

#         @qml.qnode(dev)
#         def circuit():
#             # Apply each operation from the QuantumTape
#             for op in decomposed_circuit.operations:
#                 op.apply(dev, wires=op.wires)
#             # Handle measurements
#             return qml.sample(qml.PauliZ(wires=range(num_wires)))

#         # Run the circuit to get samples
#         samples = circuit()

#         # Convert samples to bitstrings
#         bitstrings = [''.join(['1' if bit < 0 else '0' for bit in sample]) for sample in samples]
#         counts = Counter(bitstrings)
#         print("Simulation with PennyLane completed successfully.\n")
#         return counts
#     except Exception as e:
#         print(f"Error during simulation with PennyLane: {e}")
#         sys.exit(1)

# def display_results(counts, top_n=10):
#     """
#     Displays the top N measurement results sorted by count.

#     Args:
#         counts (dict): Measurement counts.
#         top_n (int): Number of top results to display.
#     """
#     print(f"Top {top_n} Measurement results:")
#     # Sort the counts by value in descending order
#     sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
#     for outcome, count in sorted_counts[:top_n]:
#         print(f"{outcome}: {count}")
#     print("\n")

# def main(qasm_file_path):
#     # Step 1: Load the QASM Circuit
#     qc = load_qasm(qasm_file_path)
#     print("--- Original Qiskit Circuit ---")
#     print(qc.draw())
#     print("\n")

#     # Step 2: Convert Qiskit Circuit to PennyLane
#     pl_circuit = convert_qiskit_to_pennylane(qc)
#     print("--- Converted PennyLane Circuit ---")
#     print(pl_circuit)
#     print("\n")

#     # Step 3: Apply Clifford-T Decomposition
#     decomposed_pl_circuit = apply_clifford_t_decomposition(pl_circuit)
#     print("--- Decomposed PennyLane Circuit ---")
#     print(decomposed_pl_circuit)
#     print("\n")

#     # Step 4: Simulate the Decomposed Circuit with PennyLane
#     counts = simulate_with_pennylane(decomposed_pl_circuit, shots=100)

#     # Step 5: Display the Simulation Results
#     display_results(counts, top_n=10)

# if __name__ == "__main__":
#     qasm_file_path = "/Users/mridul.sarkar/Documents/BlueQubitHackathon/circuit_2_30q.qasm"
#     main(qasm_file_path)
import sys

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def load_qasm(file_path):
    try:
        qc = QuantumCircuit.from_qasm_file(file_path)
        print("QASM file loaded successfully.\n")
        return qc
    except Exception as e:
        print(f"Error loading QASM file: {e}")
        sys.exit(1)

def apply_clifford_t_decomposition_qiskit(qc):
    try:
        # Transpile to Clifford+T basis
        decomposed_qc = transpile(qc, basis_gates=['h', 's', 'sdg', 't', 'tdg', 'cx'], optimization_level=3)
        print("Clifford-T decomposition applied successfully.\n")
        return decomposed_qc
    except Exception as e:
        print(f"Error during Clifford-T decomposition with Qiskit: {e}")
        sys.exit(1)

def simulate_with_qiskit(decomposed_qc, shots=1):
    try:
        simulator = AerSimulator(method='extended_stabilized')

        print("Running simulation...")
        result = simulator.run(decomposed_qc, shots=shots).result()
        print("Simulation completed.\n")

        counts = result.get_counts(decomposed_qc)
        print("Measurement counts obtained.\n")
        return counts
    except Exception as e:
        print(f"Error during simulation with Qiskit: {e}")
        sys.exit(1)

def display_results_qiskit(counts):
    print("Measurement results:")
    for outcome in sorted(counts):
        print(f"{outcome}: {counts[outcome]}")
    print("\n")

def main(qasm_file_path):
    # Step 1: Load the QASM Circuit
    qc = load_qasm(qasm_file_path)
    print("--- Original Qiskit Circuit ---")
    print(qc.draw())
    print("\n")

    # Step 2: Apply Clifford-T Decomposition with Qiskit
    decomposed_qc = apply_clifford_t_decomposition_qiskit(qc)
    print("--- Decomposed Qiskit Circuit ---")
    print(decomposed_qc.draw())
    print("\n")

    # Step 3: Simulate the Decomposed Circuit with Qiskit
    counts = simulate_with_qiskit(decomposed_qc, shots=100)

    # Step 4: Display the Simulation Results
    display_results_qiskit(counts)

if __name__ == "__main__":
    qasm_file_path = './circuit_2_42q.qasm'
    main(qasm_file_path)
