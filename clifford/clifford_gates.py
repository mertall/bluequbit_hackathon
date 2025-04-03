import math
import re

# Define the Clifford angles (multiples of π/2)
clifford_angles = [0, math.pi/2, math.pi, 3*math.pi/2]

# Function to find the closest Clifford angle
def closest_clifford(angle):
    # Wrap angle between 0 and 2*pi
    angle = angle % (2 * math.pi)
    closest = min(clifford_angles, key=lambda x: abs(x - angle))
    return closest

# File paths
input_qasm_path = '/Users/mridul.sarkar/Documents/BlueQubitHackathon/circuit_1_30q.qasm'
output_qasm_path = '/Users/mridul.sarkar/Documents/BlueQubitHackathon/circuit_1_30q_clifford.qasm'

# Read the original circuit from the QASM file as text
with open(input_qasm_path, 'r') as file:
    original_circuit = file.read()

# Split the circuit into lines
lines = original_circuit.strip().split('\n')

# Initialize a list to hold the modified circuit
modified_circuit = []

for line in lines:
    line = line.strip()
    
    # Replace rz gates
    rz_match = re.match(r"rz\(([\d\.\-eE]+)\)\s+q\[(\d+)\];", line)
    if rz_match:
        angle = float(rz_match.group(1))
        qubit = rz_match.group(2)
        new_angle = closest_clifford(angle)
        modified_circuit.append(f"rz({new_angle}) q[{qubit}];")
        continue
    
    # Replace sx gates
    sx_match = re.match(r"sx\s+q\[(\d+)\];", line)
    if sx_match:
        qubit = sx_match.group(1)
        # Decompose 'sx' into Clifford gates: H, S, H
        modified_circuit.append(f"h q[{qubit}];")
        modified_circuit.append(f"s q[{qubit}];")
        modified_circuit.append(f"h q[{qubit}];")
        continue
    
    # Keep other gates unchanged
    modified_circuit.append(line)

# Join the modified circuit back into a single string
new_circuit = '\n'.join(modified_circuit)

# Save the modified circuit to a new QASM file
with open(output_qasm_path, 'w') as file:
    file.write(new_circuit)

print(f"Modified circuit saved to '{output_qasm_path}'")
