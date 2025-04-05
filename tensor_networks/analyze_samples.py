import numpy as np
from collections import defaultdict, Counter
import matplotlib.pyplot as plt

def majority_vote_from_file(filename, num_qubits):
    """
    Reads a text file of bitstrings and returns the final bitstring
    computed by taking a bitwise majority vote.

    Args:
        filename (str): Path to the text file containing bitstrings.
        num_qubits (int): Length of each bitstring.
        
    Returns:
        str: The final bitstring determined by majority vote.
    """
    # Initialize a list of dictionaries for each bit position.
    bit_counts = [defaultdict(int) for _ in range(num_qubits)]
    total_samples = 0

    # Open the file and process line-by-line to minimize memory usage.
    with open(filename, 'r') as f:
        for line in f:
            sample = line.strip()
            # Ignore empty lines or lines with unexpected length.
            if len(sample) != num_qubits:
                continue
            total_samples += 1
            for i, bit in enumerate(sample):
                bit_counts[i][bit] += 1

    # Compute the majority bit for each position.
    final_bits = []
    for i in range(num_qubits):
        count_0 = bit_counts[i].get('0', 0)
        count_1 = bit_counts[i].get('1', 0)
        # In case of tie, choose '1' (or '0' if preferred)
        if count_1 > count_0:
            final_bits.append('1')
        if count_0 > count_1:
            final_bits.append('0')

    print(f"Total samples processed: {total_samples}")
    return ''.join(final_bits)

def check_repeats_from_file(filename, num_qubits):
    """
    Reads the file and returns a dictionary of bitstrings that appear more than once.
    """
    counter = Counter()
    with open(filename, 'r') as f:
        for line in f:
            sample = line.strip()
            if len(sample) == num_qubits:
                counter[sample] += 1
    # Filter to include only those with count > 1
    repeats = {b: c for b, c in counter.items() if c > 1}
    return repeats

if __name__ == "__main__":
    filename = "./tensor_networks/samples.txt"  # File with your bitstring samples
    num_qubits = 60  # Adjust based on your circuit

    # Compute and print the final bitstring via majority vote.
    final_bitstring = majority_vote_from_file(filename, num_qubits)
    print(f"Final bitstring (majority vote):\n{final_bitstring}")

    # Check for any repeated bitstrings and print them.
    repeats = check_repeats_from_file(filename, num_qubits)
    if repeats:
        print("\nRepeated bitstrings found:")
        for bit, count in repeats.items():
            print(f"{bit} → {count} occurrences")
    else:
        print("\nNo repeated bitstrings found.")
