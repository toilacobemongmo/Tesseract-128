#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tesseract-128: Master Verification & Reproduction Script
Reproduces core security claims, test vectors, and MILP cryptanalysis bounds.
"""

import sys
import os
import subprocess

def run_step(desc, cmd):
    print(f"\n{'='*70}")
    print(f" [*] {desc}")
    print(f"{'='*70}")
    print(f"Command: {cmd}\n")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"[!] Warning: Step exited with code {res.returncode}")
    return res.returncode

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root)

    print("\n" + "#"*70)
    print("  TESSERACT-128: REPRODUCIBILITY & SECURITY EVALUATION SUITE")
    print("#"*70)

    # 1. Compile and run test vectors
    test_exe = "test_vectors.exe" if sys.platform == "win32" else "./test_vectors"
    compile_cmd = f"gcc -O3 -Iinclude src/rubik4d.c tests/test_vectors.c -o {test_exe}"
    run_step("1. Compiling & Executing Known-Answer Test Vectors", f"{compile_cmd} && {test_exe}")

    # 2. Run MILP Differential Search
    diff_script = os.path.join("cryptanalysis", "milp_differential.py")
    if os.path.exists(diff_script):
        run_step("2. Running PuLP MILP Differential Cryptanalysis Lower Bounds", f"{sys.executable} {diff_script}")

    # 3. Run MILP Linear Search
    lin_script = os.path.join("cryptanalysis", "milp_linear.py")
    if os.path.exists(lin_script):
        run_step("3. Running PuLP MILP Linear Cryptanalysis Lower Bounds", f"{sys.executable} {lin_script}")

    # 4. Clean up test binary
    if os.path.exists(test_exe):
        try:
            os.remove(test_exe)
        except OSError:
            pass

    print("\n" + "#"*70)
    print("  [+] All verification procedures completed.")
    print("#"*70 + "\n")

if __name__ == "__main__":
    main()
