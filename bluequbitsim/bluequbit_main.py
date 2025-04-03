import bluequbit
from qiskit import QuantumCircuit


bq = bluequbit.init("<API KEY>")



# Load your circuits from the QASM files
print("Loading 30-qubit circuit from QASM file...")
qc_30q = QuantumCircuit.from_qasm_file('./circuit_1_30q.qasm')
print("30-qubit circuit loaded.\n")

# Run the simulation
print("Running simulation...")
result = bq.run(qc_30q, shots=100)
print("Simulation completed.")

counts = result.get_counts()
print(counts)
print("Measurement counts obtained.\n")

# Find the hidden bitstring with the highest counts
def find_hidden_bitstring(counts):
    print("Finding hidden bitstring with the highest counts...")
    # Find the bitstring with the maximum count
    hidden_bitstring = max(counts, key=counts.get)
    print("Hidden bitstring found.\n")
    return hidden_bitstring

hidden_bitstring_30q = find_hidden_bitstring(counts)

print("Hidden bitstring for 30-qubit circuit:", hidden_bitstring_30q)
