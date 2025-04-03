import re
from collections import OrderedDict
from graph_builder import load_qasm_file

# Define the qubit indices to exclude
exclude_qubits = {'33', '12', '23', '28', '29', '30', '31'}

# Sample input circuit as a multi-line string
# Replace this string with your actual circuit code
file_path = "/Users/mridul.sarkar/Documents/BlueQubitHackathon/circuit_2_42q.qasm"
with open(file_path, 'r') as file:
            circuit = file.read()
# Step 1: Remove lines involving excluded qubits
def remove_excluded_qubits(circuit_str, excluded):
    """
    Removes any lines from the circuit string that involve the excluded qubits.
    
    Parameters:
    - circuit_str (str): The original circuit as a string.
    - excluded (set of str): Set of qubit indices to exclude.
    
    Returns:
    - str: The circuit string with excluded qubit operations removed.
    """
    # Split the circuit into individual lines
    lines = circuit_str.strip().split('\n')
    # Prepare a list to hold lines that do not involve excluded qubits
    filtered_lines = []
    # Compile a regex pattern to detect operations involving excluded qubits
    # This pattern matches any occurrence of q[index] where index is in excluded
    pattern = re.compile(r'q\[(%s)\]' % '|'.join(map(re.escape, excluded)))
    
    for line in lines:
        # If the line does not contain any excluded qubit, keep it
        if not pattern.search(line):
            filtered_lines.append(line)
        else:
            print(f"Excluding line: {line}")
    
    # Reconstruct the circuit string
    return '\n'.join(filtered_lines)

# Apply the exclusion
filtered_circuit = remove_excluded_qubits(circuit, exclude_qubits)

# Optional: Print the filtered circuit
print("\nFiltered Circuit (Excluded Qubits Removed):")
print(filtered_circuit)

# Step 2: Extract all unique qubit indices in the order they appear
qubit_pattern = re.compile(r'q\[(\d+)\]')
qubits = qubit_pattern.findall(filtered_circuit)
unique_qubits = list(OrderedDict.fromkeys(qubits))  # Preserves order and removes duplicates

# Check if the number of unique qubits exceeds 35
max_qubits = 35  # 0..34 inclusive
if len(unique_qubits) > max_qubits:
    print(f"\nError: Number of unique qubits ({len(unique_qubits)}) exceeds the limit of {max_qubits}.")
    # Optionally, handle this scenario as needed
    # For now, we'll proceed by truncating, but you may need a different strategy
    unique_qubits = unique_qubits[:max_qubits]
    print(f"Proceeding with the first {max_qubits} qubits.")

# Step 3: Create a mapping from old indices to new indices (0..34)
mapping = {old: str(new) for new, old in enumerate(unique_qubits)}
print("\nQubit Mapping:")
for old, new in mapping.items():
    print(f"q[{old}] -> q[{new}]")

# Step 4: Replace all qubit indices in the circuit
def replace_qubits(match, mapping_dict):
    """
    Replaces the old qubit index with the new qubit index based on the mapping.
    
    Parameters:
    - match (re.Match): The regex match object.
    - mapping_dict (dict): Mapping from old qubit indices to new qubit indices.
    
    Returns:
    - str: The replacement string with the new qubit index.
    """
    old_index = match.group(1)
    new_index = mapping_dict.get(old_index, old_index)  # Keep unchanged if not in mapping
    return f'q[{new_index}]'

# Apply the replacement using a lambda to pass the mapping dictionary
remapped_circuit = qubit_pattern.sub(lambda m: replace_qubits(m, mapping), filtered_circuit)

# Optional: If you want to see the remapped circuit
print("\nRemapped Circuit:")
print(remapped_circuit)

# Step 5: Replace measurement operations if necessary
# Assuming measurements are in the format: measure q[i] -> c[j];
# If classical bits c[j] also need remapping, similar steps can be applied
# For now, we'll assume classical bits remain the same

# Save the remapped circuit to a new file or overwrite the existing one
with open('remapped_circuit.qasm', 'w') as file:
    file.write(remapped_circuit)

print("\nRemapping complete. The remapped circuit has been saved to 'remapped_circuit.qasm'.")
