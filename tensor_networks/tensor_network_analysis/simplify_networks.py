import quimb.tensor as qtn
import numpy as np
import cotengra as ctg
import itertools
import os
# Setup: Initialize the circuit with 60 qubits and load the QASM file.
circ = qtn.Circuit(N=60)
print("Loading circuit...")
circ = circ.from_openqasm2_file(
    '/Users/mridul.sarkar/Documents/BlueQubitHackathon/circuit_3_60q.qasm'
)
print("Circuit loaded.\n")


# Create a folder to save the parameter tuning graphs if it doesn't exist
output_folder = './parameter_tuning_graphs'
os.makedirs(output_folder, exist_ok=True)

# Iterate through permutations of "ACDRS", including single values
elements = "ACDRS"
for length in range(1, len(elements) + 1):
    for perm in itertools.permutations(elements, length):
        simplify_sequence = ''.join(perm)
        print(f"Processing simplify_sequence: {simplify_sequence}")
        
        # Generate the tensor network and plot
        tn = circ.amplitude_rehearse(simplify_sequence=simplify_sequence)['tn']
        plot = tn.draw(color=[f'I{q}' for q in range(60)])
        
        # Save the plot to the output folder
        output_file = os.path.join(output_folder, f"graph_{simplify_sequence}.png")
        plot.savefig(output_file)
        print(f"Saved graph to {output_file}")
