import numpy as np
from collections import defaultdict

def compute_majority_vote(bit_counts, num_qubits):
    """Return the majority vote bitstring from current bit counts."""
    final_bits = []
    for i in range(num_qubits):
        count_0 = bit_counts[i].get('0', 0)
        count_1 = bit_counts[i].get('1', 0)
        # In case of a tie, we choose '1'
        final_bits.append('1' if count_1 >= count_0 else '0')
    return ''.join(final_bits)

def lines_until_target(filename, num_qubits, target_bitstring):
    """
    Reads bitstring samples from a file and returns the number of lines
    processed until the bitwise majority vote equals the target bitstring.

    Args:
        filename (str): Path to the text file containing bitstring samples.
        num_qubits (int): The expected length of each bitstring.
        target_bitstring (str): The known correct bitstring.
        
    Returns:
        int: The number of lines processed until the majority vote equals the target.
    """
    # Initialize bit counts for each qubit position.
    bit_counts = [defaultdict(int) for _ in range(num_qubits)]
    lines_processed = 0

    with open(filename, 'r') as f:
        for line in f:
            sample = line.strip()
            if len(sample) != num_qubits:
                # Skip any line that does not match the expected length.
                continue
            lines_processed += 1
            for i, bit in enumerate(sample):
                bit_counts[i][bit] += 1

            # Compute current majority vote from counts.
            current_vote = compute_majority_vote(bit_counts, num_qubits)
            if current_vote == target_bitstring:
                return lines_processed

    # If target is never reached, return total lines processed.
    return lines_processed

if __name__ == "__main__":
    # Specify the file path and parameters.
    filename = "/Users/mridul.sarkar/Documents/BlueQubitHackathon/tensor_networks/samples.txt"
    num_qubits = 60
    target_bitstring = "110101001011010101111001011100001110101101111010100110110001"
    
    lines_needed = lines_until_target(filename, num_qubits, target_bitstring)
    print(f"Target bitstring achieved after processing {lines_needed} samples.")
