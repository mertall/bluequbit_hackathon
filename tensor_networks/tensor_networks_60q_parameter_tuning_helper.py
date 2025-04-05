import copy
import quimb.tensor as qtn
import numpy as np
import cotengra as ctg
import time
import itertools
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
import os
import tempfile

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
        final_bits.append('1' if count_1 > count_0 else '0')
    return ''.join(final_bits)

def run_experiment(tn_circuit, optimizer_lib, group_size, simplify_sequence, sample_batch_size, target_bitstring, num_samples=3):
    """
    For a given set of parameters:
      - Create a new contraction optimizer with the specified optimizer type using a unique temporary directory.
      - Work on a deep copy of the circuit to avoid state reuse.
      - Rehearse the contraction path for the given group size and simplify sequence.
      - Run the sampling step (num_samples times) to compute the average sample time.
      - Then, continuously sample while updating per-qubit counts until the majority vote equals the target bitstring.
      - Return the average sample time, time to target, and the number of samples taken.
    """
    # Create a local copy of the circuit
    local_circuit = copy.deepcopy(tn_circuit)
    
    # Create a unique temporary directory for this optimizer instance to avoid cached paths
    temp_dir = tempfile.mkdtemp(prefix=f"optimizer_{optimizer_lib}_")
    opt = ctg.ReusableHyperOptimizer(
        parallel=True,
        optlib=optimizer_lib,
        max_time="rate:1e8",
        directory=temp_dir,
        progbar=False,
    )
    
    # Rehearse the contraction path.
    local_circuit.sample_gate_by_gate_rehearse(
        group_size=group_size,
        optimize=opt,
        simplify_sequence=simplify_sequence
    )
    
    # Measure average sample time.
    sample_times = []
    rng = np.random.default_rng(42)
    for _ in range(num_samples):
        start = time.perf_counter()
        for _ in local_circuit.sample_gate_by_gate(
                sample_batch_size,
                group_size=group_size,
                optimize=opt,
                simplify_sequence=simplify_sequence,
                seed=rng):
            pass
        end = time.perf_counter()
        sample_times.append(end - start)
    avg_sample_time = np.mean(sample_times)
    
    # Measure time and samples to reach the target bitstring.
    num_qubits = len(target_bitstring)
    position_counts = [defaultdict(int) for _ in range(num_qubits)]
    found = False
    samples_count = 0
    start_target = time.perf_counter()
    rng_target = np.random.default_rng(42)
    while not found:
        for b in local_circuit.sample_gate_by_gate(
                sample_batch_size,
                group_size=group_size,
                optimize=opt,
                simplify_sequence=simplify_sequence,
                seed=rng_target):
            samples_count += 1
            for i, bit in enumerate(b):
                position_counts[i][bit] += 1
            current_vote = compute_majority_vote(position_counts, num_qubits)
            if current_vote == target_bitstring:
                found = True
                break
    end_target = time.perf_counter()
    time_to_target = end_target - start_target

    return avg_sample_time, time_to_target, samples_count

def main_tuning():
    # --- Load the circuit ---
    print("Loading circuit...")
    circ = qtn.Circuit(N=60)
    tn_circuit = circ.from_openqasm2_file('./circuit_3_60q.qasm')
    print("Circuit loaded.")
    
    # --- Define the parameter grid ---
    optimizer_types = ["optuna", "nevergrad"]
    simplify_sequences = ["ADCRS", "DCRS", "CRS", "CR", "C", "RS", "S"]
    group_size_values = [5, 10, 15, 20, 25]
    sample_batch_size_values = [1, 5, 10]
    
    # Define the target bitstring (60 bits long).
    target_bitstring = "110101001011010101111001011100001110101101111010100110110001"
    
    results = []
    # Iterate over all parameter combinations.
    for optimizer_lib, simplify_sequence, group_size, sample_batch_size in itertools.product(
            optimizer_types, simplify_sequences, group_size_values, sample_batch_size_values):
        try:
            print(f"Testing: optimizer={optimizer_lib}, simplify_sequence={simplify_sequence}, "
                  f"group_size={group_size}, sample_batch_size={sample_batch_size}")
            avg_time, time_to_target, samples_count = run_experiment(
                tn_circuit, optimizer_lib, group_size, simplify_sequence,
                sample_batch_size, target_bitstring, num_samples=3)
            results.append({
                "optimizer": optimizer_lib,
                "simplify_sequence": simplify_sequence,
                "group_size": group_size,
                "sample_batch_size": sample_batch_size,
                "avg_sample_time": avg_time,
                "time_to_target": time_to_target,
                "samples_to_target": samples_count
            })
            print(f"  -> Avg sample time: {avg_time:.4f} sec, Time to target: {time_to_target:.4f} sec, Samples: {samples_count}\n")
        except Exception as e:
            print(f"Failed for parameters {optimizer_lib}, {simplify_sequence}, group_size={group_size}, "
                  f"sample_batch_size={sample_batch_size} with error: {e}")
            continue
    
    df = pd.DataFrame(results)
    print("\nSummary of results:")
    print(df)
    
    # --- Plotting Heatmaps ---
    output_dir = "tensor_networks/parameter_tuning_graphs"
    os.makedirs(output_dir, exist_ok=True)
    
    metrics = [("avg_sample_time", "Avg Sample Time (sec)"),
               ("time_to_target", "Time to Target (sec)"),
               ("samples_to_target", "Samples to Target")]
    
    fig, axes = plt.subplots(len(optimizer_types), len(simplify_sequences)*len(metrics),
                             figsize=(20, 8), squeeze=False)
    
    for i, optimizer_lib in enumerate(optimizer_types):
        for j, simplify_sequence in enumerate(simplify_sequences):
            for k, (metric, label) in enumerate(metrics):
                ax = axes[i][j*len(metrics)+k]
                pivot = df[(df["optimizer"] == optimizer_lib) &
                           (df["simplify_sequence"] == simplify_sequence)].pivot(
                    index="group_size", columns="sample_batch_size", values=metric)
                cax = ax.imshow(pivot.values, interpolation='nearest', cmap='viridis')
                ax.set_title(f"{optimizer_lib}, {simplify_sequence}\n{label}")
                ax.set_xlabel("Sample Batch Size")
                ax.set_ylabel("Group Size")
                ax.set_xticks(np.arange(len(sample_batch_size_values)))
                ax.set_xticklabels(sample_batch_size_values)
                ax.set_yticks(np.arange(len(group_size_values)))
                ax.set_yticklabels(group_size_values)
                for (x, y), value in np.ndenumerate(pivot.values):
                    ax.text(x, y, f"{value:.2f}", ha='center', va='center', color='white')
                fig.colorbar(cax, ax=ax, label=label)
    
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "sampling_performance_heatmaps.png"), dpi=300)
    plt.close(fig)

if __name__ == '__main__':
    main_tuning()
