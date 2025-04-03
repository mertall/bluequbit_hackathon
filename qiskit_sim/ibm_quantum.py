import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService
# If you did not previously save your credentials, use the following line instead:
service = QiskitRuntimeService(channel="ibm_quantum", token="")
 
backend = service.least_busy(simulator=False, operational=True)


# Load the quantum circuit from the QASM file
qc = QuantumCircuit.from_qasm_file('./circuit_1_30q_clifford.qasm')

# Transpile the circuit for the selected backend
print("Transpiling circuit for IBM backend...")
transpiled_qc = transpile(qc, backend=backend, optimization_level=3)
print("Circuit transpiled successfully.")

# Execute the transpiled circuit on the backend
print("Submitting job to IBM backend...")
job = backend.run(transpiled_qc, shots=10000)

# Wait for the job to complete and retrieve results
result = job.result()

# Get the measurement counts
counts = result.get_counts(transpiled_qc)
print("Measurement counts obtained.\n")
# Print the measurement results
# print("\nMeasurement results:")
# for outcome in sorted(counts):
#     print(f"{outcome}: {counts[outcome]}")

    # **New Addition:** Find and display the most occurring bit string
if counts:
    # Identify the bit string with the maximum count
    most_frequent_bitstring = max(counts, key=counts.get)
    max_count = counts[most_frequent_bitstring]
    
    # Calculate the percentage occurrence
    percentage = (max_count / sum(counts.values())) * 100
    
    print("\n**Most Occurring Bit String:**")
    print(f"{most_frequent_bitstring}: {max_count} counts ({percentage:.2f}%)")
else:
    print("\nNo measurement counts were returned.")
