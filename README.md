# Tesseract-128

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Standard: C99](https://img.shields.io/badge/Standard-C99-informational.svg)]()
[![Solvers: PuLP%20%2F%20CBC](https://img.shields.io/badge/Solvers-PuLP%20%2F%20CBC-green.svg)]()

> **Tesseract-128: A 128-Bit Symmetric Block Cipher Integrating 4D Hypercube Permutations and ARX Diffusion for Constrained Telemetry Networks**  
> *Author:* Hao Gia Nguyen  
> *Affiliation:* Faculty of Information Security, Posts and Telecommunications Institute of Technology (PTIT), Hanoi, Vietnam  
> *Contact:* `haong.b24at088@stu.ptit.edu.vn`

---

## Overview

**Tesseract-128** is an ultra-compact, provably secure 128-bit symmetric block cipher (and its authenticated encryption mode **Tesseract-GCM**) specifically engineered for resource-constrained telemetry and embedded platforms that lack hardware AES-NI acceleration—such as ARM Cortex-M microcontrollers, embedded RISC-V cores, and automotive Electronic Control Units (ECUs).

On platforms without hardware cryptographic instructions, software AES forces an unfavorable trade-off: 4 KB precomputed lookup tables (T-tables) provide acceptable throughput but exhaust small embedded caches and expose timing vulnerabilities to cache-collision attacks, whereas table-free finite-field matrix multiplications incur severe computational penalties.

Tesseract-128 eliminates this trade-off by coupling spatial permutations on a 4D hypercube $\{0,1\}^4$ (discrete double-isoclinic rotations from the Lie group $SO(4)$) with 32-bit Addition-Rotation-XOR (ARX) modular diffusion:
- **Ultra-Compact Table Footprint:** Requires only **192 bytes** of static lookup tables (21 times smaller than AES T-tables), fitting entirely within a single cache line or scratchpad SRAM.
- **Provable Differential & Linear Bounds:** Mixed-Integer Linear Programming (MILP) proofs guarantee at least **22 active S-boxes** ($P_{\text{diff}} \le 2^{-132} < 2^{-128}$) and **108 active S-boxes** against linear cryptanalysis across 8 rounds.
- **Robust Security Margin:** Automated miss-in-the-middle searches establish that impossible differential, zero-correlation, and integral distinguishers terminate by round 4, securing a comfortable **4-round safety margin**.
- **Embedded & Telemetry Speedup:** Delivers **20.20 cycles/byte** in scalar C, outperforming software AES-128 by 23.0%. On 64-byte automotive CAN-FD telemetry frames, it reduces encryption latency by **$2.88\times$** (1,267 cycles vs 3,642 cycles for software AES).
- **Vector Acceleration:** Multimedia byte-shuffle instructions (`pshufb`) scale CTR throughput to **254.18 MB/s** and authenticated GCM to **208.80 MB/s**.

---

## Repository Structure

```
Tesseract-128/
├── LICENSE                     # MIT Open-Source License
├── README.md                   # Technical documentation and reproduction guide
├── Makefile                    # Standard build automation
├── run_all.py                  # Single-command automated verification suite
├── include/                    # C/C++ Header specifications
│   ├── rubik4d.h               # Core Tesseract-128 cipher API
│   ├── rubik4d_simd.h          # AVX2/SSSE3 vector intrinsics
│   ├── rubik4d_gcm.h           # Galois/Counter Mode (AEAD) specification
│   ├── aes128.h                # Reference software AES baseline
│   ├── chacha20.h              # Reference ChaCha20 baseline
│   ├── simon128.h              # Reference SIMON-128 baseline
│   └── speck128.h              # Reference SPECK-128 baseline
├── src/                        # Portable C implementation sources
│   ├── rubik4d.c               # Constant-time scalar C engine
│   ├── rubik4d_simd.c          # Vectorized SIMD pshufb implementation
│   ├── rubik4d_gcm.c           # Constant-time GHASH & GCM engine
│   ├── aes128.c                # AES reference implementation
│   ├── chacha20.c              # ChaCha20 reference implementation
│   ├── simon128.c              # SIMON reference implementation
│   └── speck128.c              # SPECK reference implementation
├── cryptanalysis/              # Automated MILP solvers & security proofs
│   ├── milp_differential.py    # PuLP/CBC differential branch active S-box solver
│   ├── milp_linear.py          # PuLP/CBC linear characteristic lower bound solver
│   ├── milp_impossible_diff.py # Automated miss-in-the-middle impossible differential search
│   ├── milp_integral.py        # Division property / multiset integral attack search
│   ├── verify_group_structure.py # Chiral hyperoctahedral group B_4^+ verification
│   └── algebraic_degree.py     # ANF algebraic degree growth analysis
└── tests/                      # Verification testbenches and performance profilers
    ├── test_vectors.c          # Known-Answer-Test (KAT) validation
    ├── test_benchmark.c        # Cycle-accurate rdtsc benchmarking harness
    ├── benchmark_iot_frames.c  # Automotive CAN-FD 64-byte frame profiling
    ├── test_key_schedule.c     # Strict Avalanche Criterion (SAC) & weak key analysis
    └── test_sensitivity.c     # Key/plaintext avalanche propagation profiling
```

---

## Quick Start & Reproduction

### Prerequisites
- **C Compiler:** `gcc` or `clang` supporting C99.
- **Python:** Python 3.8+ with `pulp` (`pip install pulp`).

### 1. Single-Command Verification
To verify known-answer test vectors and execute the automated MILP solvers:
```bash
python run_all.py
```

### 2. Building & Running Tests via Makefile
```bash
# Build test vectors and benchmark binaries
make all

# Run Known-Answer Test Vectors (KAT)
make test

# Run software throughput & cycle benchmarks
make benchmark
```

---

## Known-Answer Test Vectors (KAT)

### Vector 1: All-Zero Input (Boundary Condition)
```text
Key               : 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
Plaintext         : 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
Ciphertext (8R)   : A7 DB 79 1E 90 1F 73 64 53 0C D6 BA 4D B0 E2 79
Verification      : PASS (Decryption matches Plaintext)
```

### Vector 2: Incremental Key with ASCII Plaintext
```text
Key               : 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
Plaintext         : 52 75 62 69 6B 34 44 20 43 69 70 68 65 72 21 21 ("Rubik4D Cipher!!")
Ciphertext (8R)   : A9 FF 91 11 33 BF BC 1A 35 D6 FD 12 5F 2F 8D 24
Verification      : PASS (Decryption matches Plaintext)
```

---

## Provable Security Bounds Summary

| Metric | Bound / Result | Analytical Significance |
| :--- | :--- | :--- |
| **Differential Active S-boxes (8R)** | $\ge 22$ active S-boxes | $P_{\text{diff}} \le 2^{-132} < 2^{-128}$ (immune to differential attacks) |
| **Linear Active S-boxes (8R)** | $\ge 108$ active S-boxes | $P_{\text{linear}} \le 2^{-108}$ (immune to linear attacks) |
| **Impossible Differential Distinguisher** | Terminates at Round 4 | 4-round security margin on 8-round cipher |
| **Integral Multiset Balance** | Terminates at Round 4 | Balanced state completely disrupted by Round 4 |
| **Strict Avalanche Criterion (SAC)** | $0.4998 \pm 0.0012$ | Meets theoretical ideal of 0.50 within 2 rounds |
| **Lookup Table Memory Footprint** | **192 bytes** | $21\times$ smaller than AES T-tables (4,096 bytes) |

---

## License

This project is licensed under the [MIT License](LICENSE).
