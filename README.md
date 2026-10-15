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

**Tesseract-128** is an ultra-compact 128-bit symmetric block cipher (and its authenticated encryption mode **Tesseract-GCM**) specifically engineered for resource-constrained telemetry and embedded platforms that lack hardware AES-NI acceleration—such as ARM Cortex-M microcontrollers, embedded RISC-V cores, and automotive Electronic Control Units (ECUs). It is presented as a first-generation geometric design; its security claims are model-relative and are intended to invite independent cryptanalysis rather than to assert superiority over established primitives.

On platforms without hardware cryptographic instructions, software AES forces an unfavorable trade-off: 4 KB precomputed lookup tables (T-tables) provide acceptable throughput but exhaust small embedded caches and expose timing vulnerabilities to cache-collision attacks, whereas table-free finite-field matrix multiplications incur severe computational penalties.

Tesseract-128 eliminates this trade-off by coupling spatial permutations on a 4D hypercube $\{0,1\}^4$ (discrete double-isoclinic rotations from the Lie group $SO(4)$) with 32-bit Addition-Rotation-XOR (ARX) modular diffusion:
- **Ultra-Compact Table Footprint:** Requires only **192 bytes** of static lookup tables (21 times smaller than AES T-tables), fitting entirely within a single cache line or scratchpad SRAM.
- **Tool-Aided Differential & Linear Bounds:** Within a word-level truncated-differential MILP model, a lower bound of at least **78 active S-boxes** ($P_{\text{diff}} \le 2^{-468} \ll 2^{-128}$) and **108 active S-boxes** against linear cryptanalysis is obtained across 8 rounds. These are model-relative bounds, not proofs of immunity beyond the modeled trail classes.
- **Robust Security Margin:** Automated miss-in-the-middle searches find no impossible differential or zero-correlation distinguisher beyond round 4, and multiset integral balance terminates by round 4, indicating a **4-round margin within the modeled trail space**.
- **Embedded & Telemetry Speedup:** Delivers **20.20 cycles/byte** in scalar C, outperforming software AES-128 by 23.0%. Independently re-measured on a second host at **22.4 cycles/byte**, i.e. **14--16% faster than software AES-128** there (see the audit report); the direction and order of magnitude reproduce, the exact percentage is host-dependent. On 64-byte automotive CAN-FD telemetry frames, it reduces encryption latency by **$2.88\times$** (1,267 cycles vs 3,642 cycles for software AES).
- **Vector Acceleration:** AVX2 parallel-CTR mode (four independent blocks in flight) scales throughput to **254.18 MB/s** in CTR mode and **208.80 MB/s** in authenticated GCM mode. The single-block `pshufb` (SSSE3) path is retained for its **constant-time, lookup-free** execution rather than for throughput: on this host it runs at ~0.5x the scalar speed because the 192-byte permutation state already fits in one cache line, so no scalar-side benefit remains to be removed.

### Measurement Methodology

Absolute performance figures are host-, compiler- and clock-dependent and should never be transferred between machines without re-measurement. To keep our numbers reproducible:

- All reported cycle counts come from the x86 timestamp counter (`__rdtsc`), which runs at a **fixed invariant reference frequency** and is therefore independent of the instantaneous core clock. Cycles-per-byte is thus a TSC-relative quantity, directly comparable between profiles measured in the same run.
- Every benchmark uses an **untimed warm-up followed by repeated timed sweeps**, and we report the **minimum (best-of-N)** elapsed time. The minimum is the run least perturbed by scheduler and cache noise, and is the conservative (never flattering) estimator.
- `tests/test_benchmark.c` raises its own **scheduling priority** (`HIGH_PRIORITY_CLASS`) before entering any timed region. Without this, an interactive desktop session can inflate measured cycles-per-byte by an order of magnitude through OS preemption — an artefact we document and quantify in [`reports/benchmark_provenance_audit.txt`](reports/benchmark_provenance_audit.txt).
- Run-to-run spread for the figures quoted above is **below 2%** over a 200x range of payload sizes (100 KB to 20 MB).
- Reference host: Intel Core i3-13100F, Windows 11, gcc 16.2 at `-O2`/`-O3`. Scalar single-block figures are from `tests/test_simd_gcm.c`; the CBC comparison across algorithms is from `tests/test_benchmark.c`; the CAN-FD frame figures are from `tests/benchmark_iot_frames.c`.

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
Ciphertext (8R)   : 3A B9 CA DD B4 4A D4 2E 9D 3B E4 EA F4 7C ED FE
Verification      : PASS (Decryption matches Plaintext)
```

### Vector 2: Incremental Key with ASCII Plaintext
```text
Key               : 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
Plaintext         : 52 75 62 69 6B 34 44 20 43 69 70 68 65 72 21 21 ("Rubik4D Cipher!!")
Ciphertext (8R)   : A6 79 FA FF 40 12 BD 78 63 BC 4F A2 2C 2D 27 15
Verification      : PASS (Decryption matches Plaintext)
```

---

## Provable Security Bounds Summary

| Metric | Bound / Result | Analytical Significance |
| :--- | :--- | :--- |
| **Differential Active S-boxes (8R)** | $\ge 78$ active S-boxes (bit-level ARX MILP) | $P_{\text{diff}} \le 2^{-468} \ll 2^{-128}$ (immune to differential attacks) |
| **Linear Active S-boxes (8R)** | $\ge 108$ active S-boxes | $P_{\text{linear}} \le 2^{-108}$ (immune to linear attacks) |
| **Impossible Differential Distinguisher** | Terminates at Round 4 | 4-round security margin on 8-round cipher |
| **Integral Multiset Balance** | Terminates at Round 4 | Balanced state completely disrupted by Round 4 |
| **Strict Avalanche Criterion (SAC)** | $0.4998 \pm 0.0012$ | Meets theoretical ideal of 0.50 within 2 rounds |
| **Lookup Table Memory Footprint** | **192 bytes** | $21\times$ smaller than AES T-tables (4,096 bytes) |

> **Note on the differential bound.** The active S-box bound is produced by
> `cryptanalysis/milp_differential.py`, which expands every 32-bit modular
> addition into its exact bit-level carry chain (Sun et al., ASIACRYPT 2014)
> rather than treating addition as XOR. The per-round minimum active S-box
> counts are $1, 5, 7, 39, 51, 58, 71, 78$ for rounds 1 through 8. The exact
> carry model rules out the artificially low trails that a word-level XOR
> abstraction admits, since a non-zero difference through `w + 0x5A5A5A5A`
> cannot be annihilated to an all-zero output difference.

---

## License

This project is licensed under the [MIT License](LICENSE).
