import quimb.tensor as qtn
import numpy as np
import cotengra as ctg

from collections import defaultdict

# Setup
circ = qtn.Circuit(N=60)
print("Loading circuit...")
tensor_network_circuit = circ.from_openqasm2_file('/Users/mridul.sarkar/Documents/BlueQubitHackathon/circuit_3_60q.qasm')

opt = ctg.ReusableHyperOptimizer(
    minimize="combo",
    reconf_opts={},
    parallel=True,
    optlib="cmaes",
    max_time="rate:1e8",
    hash_method="b",
    directory=True,
    progbar=True,
)

# Rehearse once
print("Optimizing contraction path...")
tensor_network_circuit.sample_gate_by_gate_rehearse(group_size=20, optimize=opt, simplify_sequence="ADCRS")

# Sample in a loop
rng = np.random.default_rng(42)
bitstring_counts = defaultdict(int)

print("Sampling bitstrings (streamed)...")
num_samples = 1000  # You can tune this based on system memory

for b in tensor_network_circuit.sample_gate_by_gate(
    num_samples,
    group_size=20,
    optimize=opt,
    seed=rng,
    simplify_sequence="ADCRS"
):
    bitstring_counts[b] += 1

# Get the most common one
most_common = max(bitstring_counts.items(), key=lambda item: item[1])
print(f"\nMost common bitstring:\n{most_common[0]} → {most_common[1]} times (out of {num_samples})")

