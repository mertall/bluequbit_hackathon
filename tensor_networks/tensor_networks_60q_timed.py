import quimb.tensor as qtn
import numpy as np
import cotengra as ctg
from collections import defaultdict
from multiprocessing import freeze_support
import time  # For timing

def format_time(seconds):
    """Return a formatted string for a time duration in minutes and seconds if > 60 sec, otherwise in seconds."""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    else:
        minutes = int(seconds // 60)
        rem_seconds = seconds % 60
        return f"{minutes} minutes {rem_seconds:.2f} seconds"

def compute_majority_vote(bit_counts, num_qubits):
    """Return the majority vote bitstring from current per-position counts."""
    final_bits = []
    for i in range(num_qubits):
        count_0 = bit_counts[i].get('0', 0)
        count_1 = bit_counts[i].get('1', 0)
        # In case of a tie, choose '1'
        final_bits.append('1' if count_1 >= count_0 else '0')
    return ''.join(final_bits)

def main():
    overall_start = time.perf_counter()
    
    # Setup: Initialize the circuit with 60 qubits and load the QASM file.
    circ = qtn.Circuit(N=60)
    print("Loading circuit...")
    load_start = time.perf_counter()
    tensor_network_circuit = circ.from_openqasm2_file(
        './circuit_3_60q.qasm'
    )
    load_end = time.perf_counter()
    print("Circuit loaded.\n")
    print(f"Loading circuit took {format_time(load_end - load_start)}.")
    
    # Setup the contraction optimizer using cotengra.
    print("Setting up contraction optimizer...")
    opt_start = time.perf_counter()
    opt = ctg.ReusableHyperOptimizer(
        parallel=True,
        optlib="optuna",  # Using optuna (or nevergrad) for faster performance.
        max_time="rate:1e8",  # Limit optimization time.
        directory=True,
        progbar=True,
    )
    opt_end = time.perf_counter()
    print(f"Contraction optimizer setup took {format_time(opt_end - opt_start)}.")
    
    # Rehearse the sampling path (pre-optimizes contraction paths for each marginal).
    print("Optimizing contraction path...")
    path_opt_start = time.perf_counter()
    rehs = tensor_network_circuit.sample_gate_by_gate_rehearse(
        group_size=10,
        optimize=opt,
        simplify_sequence="ADCRS"  # Using "ADCRS" for simplification.
    )
    path_opt_end = time.perf_counter()
    print(f"Contraction path optimization took {format_time(path_opt_end - path_opt_start)}.")
    
    # Define target bitstring and number of qubits.
    target_bitstring = "110101001011010101111001011100001110101101111010100110110001"
    num_qubits = 60

    # Prepare to continuously sample and save each bitstring to a file.
    output_file = "./tensor_networks/samples.txt"
    with open(output_file, "a") as f:
        print("Starting continuous sampling and appending to file...")
        sample_loop_start = time.perf_counter()
        # Maintain position-wise counts for majority vote.
        position_counts = [defaultdict(int) for _ in range(num_qubits)]
        rng = np.random.default_rng(42)
        sample_batch_size = 1  # One sample per batch.
        sample_count = 0

        # Continuous sampling loop.
        while True:
            sample_iter_start = time.perf_counter()
            # Generate one sample.
            for b in tensor_network_circuit.sample_gate_by_gate(
                sample_batch_size,
                group_size=10,
                optimize=opt,
                simplify_sequence="ADCRS",
                seed=rng
            ):
                sample_iter_end = time.perf_counter()
                sample_time = sample_iter_end - sample_iter_start
                sample_count += 1
                print(f"Sample {sample_count}: {b} (took {format_time(sample_time)})")
                
                # Write sample to file.
                f.write(b + "\n")
                f.flush()  # Ensure persistence in case of interruption.
                
                # Update per-qubit counts.
                for i, bit in enumerate(b):
                    position_counts[i][bit] += 1
                
                # Check current majority vote.
                current_vote = compute_majority_vote(position_counts, num_qubits)
                if current_vote == target_bitstring:
                    solution_time = time.perf_counter() - sample_loop_start
                    print(f"\nTarget bitstring achieved after {sample_count} samples in {format_time(solution_time)}.")
                    return

                # Reset timer for next sample.
                sample_iter_start = time.perf_counter()
                
            # Log total sampling time every 10 samples.
            if sample_count % 10 == 0:
                current_time = time.perf_counter()
                elapsed = current_time - sample_loop_start
                print(f"Processed {sample_count} samples in {format_time(elapsed)}.")
    
    overall_end = time.perf_counter()
    print(f"Overall process took {format_time(overall_end - overall_start)}.")

if __name__ == '__main__':
    freeze_support()
    main()
