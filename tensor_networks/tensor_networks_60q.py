import quimb.tensor as qtn
import numpy as np
import cotengra as ctg
from collections import defaultdict
from multiprocessing import freeze_support

def main():
    # Setup: Initialize the circuit with 60 qubits and load the QASM file.
    circ = qtn.Circuit(N=60)
    print("Loading circuit...")
    tensor_network_circuit = circ.from_openqasm2_file(
        '/Users/mridul.sarkar/Documents/BlueQubitHackathon/circuit_3_60q.qasm'
    )
    print("Circuit loaded.\n")

    # Setup the contraction optimizer using cotengra.
    opt = ctg.ReusableHyperOptimizer(
        parallel=True,
        optlib="optuna",  # Using nevergrad for faster performance.
        max_time="rate:1e8",  # Limit optimization time.
        directory=True,
        progbar=True,
    )

    # Rehearse the sampling path (pre-optimizes contraction paths for each marginal).
    print("Optimizing contraction path...")
    rehs = tensor_network_circuit.sample_gate_by_gate_rehearse(
        group_size=10,
        optimize=opt,
        simplify_sequence="ADCRS"  # Use a simpler sequence to reduce overhead.
    )
    
    # Prepare to continuously sample and save each bitstring to a file.
    output_file = "./tensor_networks/samples.txt"
    # Open file in append mode (creates the file if it doesn't exist).
    with open(output_file, "a") as f:
        print("Starting continuous sampling and appending to file...")
        bitstring_counts = defaultdict(int)
        rng = np.random.default_rng(42)
        sample_batch_size = 1  # Number of samples per batch.
        
        # Continuous sampling loop.
        while True:
            for b in tensor_network_circuit.sample_gate_by_gate(
                sample_batch_size,
                group_size=10,
                optimize=opt,
                simplify_sequence="ADCRS",
                seed=rng
            ):
                # Update count (optional, for later analysis)
                bitstring_counts[b] += 1
                # Append the sampled bitstring to the file.
                f.write(b + "\n")
                f.flush()  # Flush to disk to ensure persistence on interruption.
                print(b)

if __name__ == '__main__':
    freeze_support()
    main()
