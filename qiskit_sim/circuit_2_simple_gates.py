import numpy as np
import random
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

qc = QuantumCircuit.from_qasm_file('/Users/mridul.sarkar/Documents/BlueQubitHackathon/circuit_2_42q.qasm')

# Execute the circuit on the qasm simulator
simulator = AerSimulator(method="matrix_product_state")
print("Transpiling circuit for simulator...")
qc = transpile(qc, simulator, optimization_level=2)
print("Circuit transpiled.")

# Run the simulation
print("Running simulation...")
result = simulator.run(qc, shots=1).result()
print("Simulation completed.")

counts = result.get_counts(qc)
print("Measurement counts obtained.\n")

# Print the measurement results
print("\nMeasurement results:")
for outcome in sorted(counts):
    print(f"{outcome}: {counts[outcome]}")
