#!/usr/bin/env python3
"""
assembler.py  -  Hack assembler (Nand to Tetris, Project 6)

Name     : Krishna Gupta
Roll no. : 2501350048      ->  K = 48
K mod 3  : 0  ->  extra feature: assembly metrics & code profiling
                  combined with complete symbol table resolution & memory mapping
                  dump and robust line-number error reporting.

Usage:
    python3 assembler.py Prog.asm            # writes Prog.hack next to Prog.asm
    python3 assembler.py Prog.asm Out.hack   # writes to Out.hack instead

How it works (two passes over the file):
    Pass 1  - throw away comments / blank lines,
              remember the ROM address of every label  (LOOP)
    Pass 2  - translate every remaining line into 16 bits.
              Unknown symbols in @xxx are variables and get RAM
              addresses 16, 17, 18, ... in order of first appearance.
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# 1. Lookup tables straight from the Hack machine-language specification
# ---------------------------------------------------------------------------

# comp  ->  7 bits:  a c1 c2 c3 c4 c5 c6
COMP = {
    "0":   "0101010", "1":   "0111111", "-1":  "0111010",
    "D":   "0001100", "A":   "0110000", "M":   "1110000",
    "!D":  "0001101", "!A":  "0110001", "!M":  "1110001",
    "-D":  "0001111", "-A":  "0110011", "-M":  "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101",
}

# dest  ->  3 bits:  d1 d2 d3   (A, D, M)
DEST = {
    "":    "000", "M":   "001", "D":   "010", "MD":  "011",
    "A":   "100", "AM":  "101", "AD":  "110", "AMD": "111",
}

# jump  ->  3 bits:  j1 j2 j3   (<0, =0, >0)
JUMP = {
    "":    "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}

# Symbols that every Hack program already knows about.
PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
}
for _i in range(16):
    PREDEFINED[f"R{_i}"] = _i

# A symbol may contain letters, digits, '_', '.', '$', ':' and may not start with a digit.
SYMBOL_RE = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")

FIRST_VARIABLE_ADDRESS = 16


# ---------------------------------------------------------------------------
# 2. Error reporting and Result Data Structures
# ---------------------------------------------------------------------------
class AsmError(Exception):
    """A problem found on one source line."""

    def __init__(self, line_no, message):
        super().__init__(f"Line {line_no}: invalid instruction - {message}")
        self.line_no = line_no


class AssembleResult(int):
    """Result object behaving as an int (instruction count) with analysis metadata."""

    def __new__(cls, count, user_labels=None, user_vars=None, a_count=0, c_count=0):
        obj = super().__new__(cls, count)
        obj.count = count
        obj.user_labels = user_labels or {}
        obj.user_vars = user_vars or {}
        obj.a_count = a_count
        obj.c_count = c_count
        return obj


# ---------------------------------------------------------------------------
# 3. Helpers
# ---------------------------------------------------------------------------
def clean(line):
    """Remove comments and ALL whitespace. Returns '' for an empty line."""
    line = line.split("//", 1)[0]            # drop everything after //
    return "".join(line.split())             # drop spaces / tabs


def read_instructions(path):
    """Pass 0: read the file, keep only real instructions, with their original line numbers."""
    instructions = []
    with open(path) as f:
        for line_no, raw in enumerate(f, start=1):
            text = clean(raw)
            if text:
                instructions.append((line_no, text))
    return instructions


def first_pass(instructions):
    """
    Build the symbol table with all labels.
    A label (LOOP) does not become an instruction; it just names the
    address of the NEXT real instruction, so we count ROM addresses as we go.
    """
    symbols = dict(PREDEFINED)
    user_labels = {}
    rom_address = 0
    for line_no, text in instructions:
        if text.startswith("("):
            if not text.endswith(")"):
                raise AsmError(line_no, f"label {text!r} is missing ')'")
            name = text[1:-1]
            if not SYMBOL_RE.match(name):
                raise AsmError(line_no, f"{name!r} is not a valid label name")
            if name in symbols:
                raise AsmError(line_no, f"label {name!r} is already defined")
            symbols[name] = rom_address
            user_labels[name] = rom_address
        else:
            rom_address += 1
    return symbols, user_labels


def translate_a(text, line_no, symbols, next_var):
    """
    @value  ->  0 + 15-bit binary value.
    Returns (binary_string, next_var, var_added). next_var is the RAM address
    the next brand-new variable will receive.
    """
    value = text[1:]
    var_added = None
    if value == "":
        raise AsmError(line_no, "'@' must be followed by a number or a symbol")
    if value.isdigit():
        number = int(value)
        if number > 32767:
            raise AsmError(line_no, f"@{number} is too large (max 32767)")
    elif SYMBOL_RE.match(value):
        if value not in symbols:                 # a new variable
            symbols[value] = next_var
            var_added = value
            next_var += 1
        number = symbols[value]
    else:
        raise AsmError(line_no, f"{value!r} is not a valid number or symbol")
    return "0" + format(number, "015b"), next_var, var_added


def translate_c(text, line_no):
    """dest=comp;jump  ->  111 + comp(7) + dest(3) + jump(3)."""
    dest, comp, jump = "", text, ""
    if "=" in comp:
        dest, comp = comp.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)
    if comp not in COMP:
        raise AsmError(line_no, f"unknown computation {comp!r}")
    if dest not in DEST:
        raise AsmError(line_no, f"unknown destination {dest!r}")
    if jump not in JUMP:
        raise AsmError(line_no, f"unknown jump {jump!r}")
    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def second_pass(instructions, symbols):
    """Translate every non-label line into a 16-bit string."""
    binary = []
    user_vars = {}
    next_var = FIRST_VARIABLE_ADDRESS
    a_count = 0
    c_count = 0
    for line_no, text in instructions:
        if text.startswith("("):                 # labels were handled in pass 1
            continue
        if text.startswith("@"):
            code, next_var, var_added = translate_a(text, line_no, symbols, next_var)
            if var_added:
                user_vars[var_added] = symbols[var_added]
            a_count += 1
        else:
            code = translate_c(text, line_no)
            c_count += 1
        binary.append(code)
    return binary, user_vars, a_count, c_count


def assemble(asm_path, hack_path):
    """Full pipeline. Raises AsmError on the first bad line."""
    instructions = read_instructions(asm_path)
    symbols, user_labels = first_pass(instructions)
    binary, user_vars, a_count, c_count = second_pass(instructions, symbols)
    with open(hack_path, "w") as f:
        f.write("\n".join(binary) + "\n")
    return AssembleResult(len(binary), user_labels, user_vars, a_count, c_count)


# ---------------------------------------------------------------------------
# 4. Command-line entry point
# ---------------------------------------------------------------------------
def main(argv):
    if len(argv) not in (2, 3):
        print("Usage: python3 assembler.py Prog.asm [Prog.hack]")
        return 2
    asm_path = argv[1]
    hack_path = argv[2] if len(argv) == 3 else os.path.splitext(asm_path)[0] + ".hack"

    if not os.path.exists(asm_path):
        print(f"Error: file not found: {asm_path}")
        return 1

    try:
        result = assemble(asm_path, hack_path)
    except AsmError as err:
        print(err)                                   # e.g.  Line 7: invalid instruction - ...
        print("No .hack file was written.")
        return 1

    print(f"OK: {result.count} instructions written to {hack_path}")
    print("Assembly Analysis & Metrics (K mod 3 = 0 feature):")
    print(f"  Total Instructions : {result.count}")
    print(f"  A-Instructions     : {result.a_count}")
    print(f"  C-Instructions     : {result.c_count}")
    if result.user_labels or result.user_vars:
        print("Symbol Resolution Table & Memory Mapping:")
        if result.user_labels:
            print("  User Labels:")
            for name, addr in sorted(result.user_labels.items(), key=lambda x: x[1]):
                print(f"    ({name}) -> ROM[{addr}]")
        if result.user_vars:
            print("  User Variables:")
            for name, addr in sorted(result.user_vars.items(), key=lambda x: x[1]):
                print(f"    @{name} -> RAM[{addr}]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
