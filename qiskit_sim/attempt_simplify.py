import sys
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def load_qasm(file_path):
    """
    Loads a QASM file into a Qiskit QuantumCircuit.
    """
    try:
        qc = QuantumCircuit.from_qasm_file(file_path)
        print("QASM file loaded successfully.\n")
        return qc
    except Exception as e:
        print(f"Error loading QASM file: {e}")
        sys.exit(1)

def decompose_non_clifford_gates(original_qc):
    """
    Decomposes 'sx' and 'cz' gates into Clifford gate sequences.
    
    Args:
        original_qc (QuantumCircuit): The original quantum circuit.
    
    Returns:
        QuantumCircuit: The decomposed quantum circuit with Clifford gates.
    """
    decomposed_qc = QuantumCircuit(original_qc.num_qubits, original_qc.num_clbits)
    
    for instruction, qargs, cargs in original_qc.data:
        if instruction.name == 'sx':
            # Replace 'sx' with 'h', 's', 'h'
            qubit = qargs[0]
            decomposed_qc.h(qubit)
            decomposed_qc.s(qubit)
            decomposed_qc.h(qubit)
        elif instruction.name == 'cz':
            # Replace 'cz' with 'h', 'cx', 'h' on target qubit
            control = qargs[0]
            target = qargs[1]
            decomposed_qc.h(target)
            decomposed_qc.cx(control, target)
            decomposed_qc.h(target)
        else:
            # Keep the gate as is
            decomposed_qc.append(instruction, qargs, cargs)
    
    print("Non-Clifford gates ('sx' and 'cz') decomposed into Clifford gate sequences.\n")
    return decomposed_qc

def simulate_with_qiskit(decomposed_qc, shots=1):
    """
    Simulates the decomposed Qiskit circuit using Qiskit's Aer simulator.
    
    Args:
        decomposed_qc (QuantumCircuit): The Clifford+T decomposed quantum circuit.
        shots (int): Number of simulation shots.
    
    Returns:
        dict: Measurement counts.
    """
    try:
        simulator = AerSimulator(method='extended_stabilizer')
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
    """
    Displays the measurement results.
    
    Args:
        counts (dict): Measurement counts.
    """
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
    
    # Step 2: Decompose Non-Clifford Gates ('sx' and 'cz') into Clifford gates
    decomposed_qc = decompose_non_clifford_gates(qc)
    print("--- Decomposed Circuit (Clifford Gates Only) ---")
    print(decomposed_qc.draw())
    print("\n")
    
    # Step 3: Simulate the Transpiled Circuit with Qiskit
    counts = simulate_with_qiskit(decomposed_qc, shots=100)  # <-- Corrected line
    
    # Step 5: Display the Simulation Results
    display_results_qiskit(counts)

if __name__ == "__main__":
    qasm_file_path = './circuit_2_42q.qasm'
    main(qasm_file_path)
