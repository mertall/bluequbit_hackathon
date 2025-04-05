import quimb.tensor as qtn
import numpy as np
import cotengra as ctg
import time
import itertools
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict

def format_time(seconds):
    """Return a formatted string for a time duration."""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    else:
        minutes = int(seconds // 60)
        rem_seconds = seconds % 60
        return f"{minutes} minutes {rem_seconds:.2f} seconds"

def compute_majority_vote(bit_counts, num_qubits):
    """Return the majority vote bitstring from position-wise counts."""
    final_bits = []
    for i in range(num_qubits):
        count_0 = bit_counts[i].get('0', 0)
        count_1 = bit_counts[i].get('1', 0)
        final_bits.append('1' if count_1 >= count_0 else '0')
    return ''.join(final_bits)

def run_experiment(tn_circuit, optimizer_lib, group_size, simplify_sequence, sample_batch_size, target_bitstring, num_samples=3):
    """
    For a given set of parameters:
      - Create a new contraction optimizer matching the optimizer type.
      - Re-run the contraction path rehearsal for the given group size and simplify sequence.
      - Run the sampling step (num_samples times) and return the average sample time.
      - Then, continuously sample while updating per-qubit counts until the majority vote equals the target bitstring.
        Return the time taken to reach the target.
    """
    # Create a new optimizer instance matching the current optimizer type.
    opt = ctg.ReusableHyperOptimizer(
        parallel=True,
        optlib=optimizer_lib,
        max_time="rate:1e8",
        directory=True,
        progbar=False,  # Disable progress bar for cleaner output.
    )
    
    # Rehearse the contraction path to ensure the optimizer is in sync with the parameters.
    tn_circuit.sample_gate_by_gate_rehearse(
        group_size=group_size,
        optimize=opt,
        simplify_sequence=simplify_sequence
    )
    
    # --- Measure average sample time ---
    sample_times = []
    rng = np.random.default_rng(42)
    for _ in range(num_samples):
        start = time.perf_counter()
        # Run the sampling; iterate over the generator to force computation.
        for _ in tn_circuit.sample_gate_by_gate(
                sample_batch_size,
                group_size=group_size,
                optimize=opt,
                simplify_sequence=simplify_sequence,
                seed=rng):
            pass
        end = time.perf_counter()
        sample_times.append(end - start)
    avg_sample_time = np.mean(sample_times)
    
    # --- Measure time to reach the target bitstring via majority vote ---
    num_qubits = len(target_bitstring)
    position_counts = [defaultdict(int) for _ in range(num_qubits)]
    found = False
    samples_count = 0
    start_target = time.perf_counter()
    
    # Use a fresh RNG for target search.
    rng_target = np.random.default_rng(42)
    while not found:
        for b in tn_circuit.sample_gate_by_gate(
                sample_batch_size,
                group_size=group_size,
                optimize=opt,
                simplify_sequence=simplify_sequence,
                seed=rng_target):
            samples_count += 1
            # Update counts for each qubit.
            for i, bit in enumerate(b):
                position_counts[i][bit] += 1
            current_vote = compute_majority_vote(position_counts, num_qubits)
            if current_vote == target_bitstring:
                found = True
                break
    end_target = time.perf_counter()
    time_to_target = end_target - start_target

    return avg_sample_time, time_to_target

def main_tuning():
    # --- Load the circuit ---
    print("Loading circuit...")
    circ = qtn.Circuit(N=60)
    # Adjust the file path as needed.
    tn_circuit = circ.from_openqasm2_file('./circuit_3_60q.qasm')
    print("Circuit loaded.")
    
    # --- Define the parameter grid ---
    optimizer_types = ["optuna", "nevergrad"]
    simplify_sequences = ["ADCRS", "DCRS"]
    group_size_values = [5, 10, 15]
    sample_batch_size_values = [1, 5, 10]
    
    # Define the target bitstring (must be 60 bits long).
    target_bitstring = "110101001011010101111001011100001110101101111010100110110001"
    
    # Create a list to store results.
    results = []
    
    # Iterate over all parameter combinations.
    for optimizer_lib, simplify_sequence, group_size, sample_batch_size in itertools.product(
            optimizer_types, simplify_sequences, group_size_values, sample_batch_size_values):
        try:
            print(f"Testing: optimizer={optimizer_lib}, simplify_sequence={simplify_sequence}, "
                  f"group_size={group_size}, sample_batch_size={sample_batch_size}")
            avg_time, time_to_target = run_experiment(tn_circuit, optimizer_lib, group_size,
                                                      simplify_sequence, sample_batch_size,
                                                      target_bitstring, num_samples=3)
            results.append({
                "optimizer": optimizer_lib,
                "simplify_sequence": simplify_sequence,
                "group_size": group_size,
                "sample_batch_size": sample_batch_size,
                "avg_sample_time": avg_time,
                "time_to_target": time_to_target
            })
            print(f"  -> Avg sample time: {avg_time:.4f} sec, Time to target: {time_to_target:.4f} sec\n")
        except Exception:
            # If any error occurs (e.g., memory error), skip this parameter combination.
            continue
    
    # Convert results to a DataFrame.
    df = pd.DataFrame(results)
    print("\nSummary of results:")
    print(df)
    
    # --- Plotting ---
    # Create a heatmap for each combination of optimizer and simplify_sequence.
    fig, axes = plt.subplots(len(optimizer_types), len(simplify_sequences)*2,
                             figsize=(16, 8), squeeze=False)
    
    # Loop over each optimizer and simplify sequence.
    for i, optimizer_lib in enumerate(optimizer_types):
        for j, simplify_sequence in enumerate(simplify_sequences):
            # Filter the data.
            pivot_time = df[(df["optimizer"] == optimizer_lib) &
                            (df["simplify_sequence"] == simplify_sequence)].pivot(
                index="group_size", columns="sample_batch_size", values="avg_sample_time")
            pivot_target = df[(df["optimizer"] == optimizer_lib) &
                              (df["simplify_sequence"] == simplify_sequence)].pivot(
                index="group_size", columns="sample_batch_size", values="time_to_target")
            
            # Plot average sample time.
            ax_time = axes[i][2*j]
            cax_time = ax_time.imshow(pivot_time.values, interpolation='nearest', cmap='viridis')
            ax_time.set_title(f"{optimizer_lib}, {simplify_sequence}:\nAvg Sample Time")
            ax_time.set_xlabel("Sample Batch Size")
            ax_time.set_ylabel("Group Size")
            ax_time.set_xticks(np.arange(len(sample_batch_size_values)))
            ax_time.set_xticklabels(sample_batch_size_values)
            ax_time.set_yticks(np.arange(len(group_size_values)))
            ax_time.set_yticklabels(group_size_values)
            for (x, y), value in np.ndenumerate(pivot_time.values):
                ax_time.text(x, y, f"{value:.2f}", ha='center', va='center', color='white')
            fig.colorbar(cax_time, ax=ax_time, label="Time (sec)")
            
            # Plot time to target.
            ax_target = axes[i][2*j+1]
            cax_target = ax_target.imshow(pivot_target.values, interpolation='nearest', cmap='viridis')
            ax_target.set_title(f"{optimizer_lib}, {simplify_sequence}:\nTime to Target")
            ax_target.set_xlabel("Sample Batch Size")
            ax_target.set_ylabel("Group Size")
            ax_target.set_xticks(np.arange(len(sample_batch_size_values)))
            ax_target.set_xticklabels(sample_batch_size_values)
            ax_target.set_yticks(np.arange(len(group_size_values)))
            ax_target.set_yticklabels(group_size_values)
            for (x, y), value in np.ndenumerate(pivot_target.values):
                ax_target.text(x, y, f"{value:.2f}", ha='center', va='center', color='white')
            fig.colorbar(cax_target, ax=ax_target, label="Time (sec)")
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main_tuning()
