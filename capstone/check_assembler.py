#!/usr/bin/env python3
"""
check_assembler.py
Cross-platform checker that compares assembler.py output with official Nand2Tetris outputs.
Works on Windows, macOS, and Linux without bash or diff.
"""
import os
import sys
import tempfile
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

programs = ["Add", "Max", "Rect", "Pong", "Box"]
all_passed = True

with tempfile.TemporaryDirectory() as tmp_dir:
    for prog in programs:
        src = os.path.join(SCRIPT_DIR, "Box.asm") if prog == "Box" else os.path.join(SCRIPT_DIR, "asm_tests", f"{prog}.asm")
        official = os.path.join(SCRIPT_DIR, "asm_tests", "official", f"{prog}.hack")
        out_hack = os.path.join(tmp_dir, f"{prog}.hack")

        # Run assembler
        cmd = [sys.executable, os.path.join(SCRIPT_DIR, "assembler.py"), src, out_hack]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            print(f"FAILED: {prog}.asm could not be assembled:")
            print(proc.stderr or proc.stdout)
            all_passed = False
            continue

        # Read both files and normalize line endings
        with open(official, "r", encoding="utf-8") as f:
            official_lines = [line.strip() for line in f if line.strip()]

        with open(out_hack, "r", encoding="utf-8") as f:
            generated_lines = [line.strip() for line in f if line.strip()]

        if official_lines == generated_lines:
            print(f"[PASS] {prog}.asm -> matches official output ({len(generated_lines)} lines)")
        else:
            print(f"[FAIL] {prog}.asm -> differs from official output!")
            print(f"  Expected {len(official_lines)} lines, got {len(generated_lines)} lines.")
            all_passed = False

if all_passed:
    print("\nAll assembler comparison tests passed successfully!")
    sys.exit(0)
else:
    print("\nSome tests failed.")
    sys.exit(1)
