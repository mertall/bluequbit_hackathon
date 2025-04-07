import quimb.tensor as qtn
from collections import Counter
# Initialize the circuit with 42 qubits.
circ = qtn.Circuit(N=42)

# Load QASM circuit.
print("Loading circuit from QASM file...")
circ = circ.from_openqasm2_file('./circuit_2_42q.qasm')
print("Circuit loaded.\n")

# Dictionary to count occurrences of each bitstring.
bitstring_counts = {}

for b in circ.sample(30):
    print(b)

# Result 110111100011100000101100001110101010011111
