# BlueQubit Hackathon
# Project Overview

This repository documents the progression of solving [[peak circuits](https://arxiv.org/abs/2404.14493)]using various computational techniques, culminating in the use of Tensor Networks for results. Below is the step-by-step evolution of the approach:

## Hackathon Work
1. **Brute Force with GPU Credits**: Leveraged GPU resources for initial brute force solutions.
2. **IBM Compiler Optimization**: Improved efficiency using IBM's compiler optimizations.
3. **Clifford Gates Translation**: Translated computations into Clifford Gates for further optimization.
4. **Graph Representation and Pruning**: Represented the problem as a graph and pruned unnecessary connections to simplify computations.

## Post-Hackathon Work (April 1st–April 3rd, 2025)
5. **Tensor Networks**: Adopted Tensor Networks, as suggested by BlueQubit, leading to the results below.

## Results

- **Circuit 1**: `111101001101110101000110100100`  
- **Circuit 2**: `110111100011100000101100001110101010011111`  
- **Circuit 3**: `110101001011010101111001011100001110101101111010100110110001`  

## Tensor Networks

Quimb lets us use tensor network techniques, which approximates the final state of complex circuits by compressing the network (via local simplifications and contraction path optimization). This allowed us to sample the circuit without needing to construct the full state vector, even for circuits with up to 60 qubits.

Below are some visuals from this work that I found really cool:

### 30 Qubit Tensor Network

![30 Qubit Tensor Network](/tensor_networks/30qubit_tensor_network.png)

### 42 Qubit Tensor Network

![42 Qubit Tensor Network](/tensor_networks/42qubit_tensor_network.png)

### 60 Qubit Tensor Network

![60 Qubit Tensor Network](/tensor_networks/60qubit_tensor_network.png)

Notice the similarity between the 30 Qubit and 60 Qubit networks. Initially, I thought they were identical until I analyzed the networks post-optimization. Below is the 60 Qubit system after optimization. The 30 Qubit system simplifies significantly after optimization. Fascinating!

### Optimized 60 Qubit Tensor Network

![Optimized 60 Qubit Tensor Network](/tensor_networks/amplitude_rehearse_ADCRS_60.png)

### Optimized 30 Qubit Tensor Network

![Optimized 30 Qubit Tensor Network](/tensor_networks/amplitude_rehearse_ADCRS_30.png)

## Tensor Network Techniques

We focus only on the 60 qubit circuit techniques as the other circuits were very simple to solve.

### Tensor Network Simplification

The circuit’s tensor network is simplified using a sequence of local simplification methods controlled by the simplify_sequence parameter. For example, using "ADCRS" applies:

- A: Antidiagonal gauge
- D: Diagonal reduction
- C: Column reduction
- R: Rank simplification
- S: Split simplification
The order matters since each operation transforms the network differently. In practice, we experiment with different sequences (e.g. "CR", "R", or the full "ADCRS") to balance contraction speed, memory usage, and numerical accuracy.

### Contraction Path Optimization

We leverage cotengra for finding efficient contraction paths. In our setup, we use a reusable hyperoptimizer with parameters tuned to our circuit’s complexity. For instance, we often choose optlib="nevergrad" or "optuna" (depending on our trade-off between exploration and speed) and set parameters such as:

minimize="combo" (a balanced cost function)
parallel=True to utilize multiple CPU cores
A limited max_time to prevent overlong optimization

### Sampling Strategy

We perform sampling using a gate-by-gate approach. This method calculates the marginal probability distribution for a small group of qubits (controlled by group_size) in sequence. The contraction paths are pre-optimized with sample_gate_by_gate_rehearse(), and then the circuit is sampled continuously.
Samples are streamed directly to a text file. Larger sample sizes led to memory leaks due to running locally.

### Final Value Extraction (60 Qubit Circuit)

For the 60-qubit circuit, after sampling and analyzing many results, the dominant bitstring is extracted via the bitwise majority vote. This final bitstring is our best estimate of the hidden bitstring. In our experiments, we observed that while the samples may differ from run to run due to noise or contraction approximations, the majority vote consolidates the signal to reveal the hidden solution.