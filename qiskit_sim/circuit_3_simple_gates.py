import numpy as np
import random
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

# # Set N and random seed
# N = 59
# random.seed(42)

# # Create quantum and classical registers
# qr = QuantumRegister(N + 1, 'q')
# cr = ClassicalRegister(N + 1, 'c')
# qc = QuantumCircuit(qr, cr)

# for k in range(860,-1,-1):
#     # Build the circuit
#     for i in range(N, -1, -1):

#         R1 = random.uniform(0, 2 * np.pi)
#         R2 = random.uniform(0, 2 * np.pi)
#         R3 = random.uniform(0, 2 * np.pi)
#         R4 = random.uniform(0, 2 * np.pi)
#         R5 = random.uniform(0, 2 * np.pi)
#         R6 = random.uniform(0, 2 * np.pi)
#         l, m = random.sample(range(N), 2)

#         theta1 = R1 + R2
#         theta2 = R4 + R5 


#         qc.rz(theta1, qr[l])
#         qc.sx(qr[l])
#         qc.x(qr[l])
#         qc.sx(qr[l])
#         qc.rz(R3, qr[l])

#         qc.rz(theta2, qr[m])
#         qc.sx(qr[m])
#         qc.x(qr[m])
#         qc.sx(qr[m])
#         qc.rz(R6, qr[m])

#         qc.cz(qr[l], qr[m])

# qc.measure(qr, cr)
qc = QuantumCircuit.from_qasm_file('/Users/mridul.sarkar/Documents/BlueQubitHackathon/circuit_3_60q.qasm')

# Execute the circuit on the qasm simulator
simulator = AerSimulator(method='matrix_product_state')
print("Transpiling circuit for simulator...")
qc = transpile(qc, simulator,optimization_level=2)
print("Circuit transpiled.")

# Run the simulation
print("Running simulation...")
result = simulator.run(qc, shots=1).result()
print("Simulation completed.")

counts = result.get_counts()
print("Measurement counts obtained.\n")
print(counts)
