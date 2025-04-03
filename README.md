# BlueQubit Hackathon
# Project Overview

This repository documents the progression of solving computational problems using various optimization techniques, culminating in the use of Tensor Networks for accurate results. Below is the step-by-step evolution of the approach:

## Hackathon Work
1. **Brute Force with GPU Credits**: Leveraged GPU resources for initial brute force solutions.
2. **IBM Compiler Optimization**: Improved efficiency using IBM's compiler optimizations.
3. **Clifford Gates Translation**: Translated computations into Clifford Gates for further optimization.
4. **Graph Representation and Pruning**: Represented the problem as a graph and pruned unnecessary connections to simplify computations.

## Post-Hackathon Work (April 1st–April 3rd, 2025)
5. **Tensor Networks**: Adopted Tensor Networks, as suggested by BlueQubit, leading to the results below.

# Results

- **Circuit 1**: `111101001101110101000110100100`  
- **Circuit 2**: `110111100011100000101100001110101010011111`  
- **Circuit 3**: `111000001011011001110011011100011110101001111010100011110110`  

# Tensor Networks

Working with Tensor Networks was an exciting and intuitive experience. Although I had not studied contraction on Tensor Networks before, I began to understand it as reducing bond dimensions between tensors using SVD (or a more computationally appropriate technique) and then contracting or solving for linear relationships between tensors to simplify the network. This simple yet powerful idea, when applied to Quantum Circuits, felt natural. Kudos to BlueQubit for setting up this challenge—it introduced me to a fascinating new concept.

Below are some visuals from this work that I found really cool:

## 30 Qubit Tensor Network

![30 Qubit Tensor Network](/tensor_networks/30qubit_tensor_network.png)

## 42 Qubit Tensor Network

![42 Qubit Tensor Network](/tensor_networks/42qubit_tensor_network.png)

## 60 Qubit Tensor Network

![60 Qubit Tensor Network](/tensor_networks/60qubit_tensor_network.png)

Notice the similarity between the 30 Qubit and 60 Qubit networks. Initially, I thought they were identical until I analyzed the networks post-optimization. Below is the 60 Qubit system after optimization. The 30 Qubit system simplifies significantly after optimization. Fascinating!

## Optimized 60 Qubit Tensor Network

![Optimized 60 Qubit Tensor Network](/tensor_networks/amplitude_rehearse_ADCRS_60.png)
