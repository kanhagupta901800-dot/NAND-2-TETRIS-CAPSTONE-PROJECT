# Capstone Project - Make the Computer Draw a Box

Krishna Gupta (2501350048)

Nand to Tetris - I (ETCCNT301)

## My K

K = last two digits of roll number = **48**

- K mod 3 = 0  -> extra assembler feature: assembly metrics & code profiling combined with symbol table resolution & memory mapping dump (reports total instruction count, A-instruction vs C-instruction breakdown, user labels with ROM addresses, and user variables with RAM addresses upon assembly, with robust line-number error reporting)
- K mod 4 = 0  -> box width = 16 x (0 + 1) = 16 pixels (1 word)
- Box starts at row 48 and is 20 rows tall (rows 48 to 67)
- First address of the box = SCREEN + 32 x 48 = 16384 + 1536 = 17920

## Files

```
CPU.hdl, Memory.hdl, Computer.hdl   -> Part A (the Hack computer)
other .hdl files                    -> my lab chips (gates, ALU, PC, Register, Bit) used by the CPU
*.tst, *.cmp, *.hack                -> official test files for Part A
assembler.py                        -> Part B (Hack assembler in Python)
asm_tests/                          -> Add, Max, Rect, Pong programs used to test the assembler
asm_tests/official/                 -> output of the official Nand2Tetris assembler for the same programs
check_assembler.py                  -> compares my assembler output with the official assembler
check_assembler.sh                  -> bash runner for check_assembler
Box.asm                             -> Part C (box program)
Box.hack                            -> Box.asm converted using my assembler
steps/                              -> how I built Box.asm step by step (dash -> wide dash -> box)
```

## How to Run

### Part A

Open the Hardware Simulator, load `CPU.tst` and run it. Same for `Memory.tst`,
`ComputerAdd.tst`, `ComputerMax.tst` and `ComputerRect.tst`.

The RAM16K, Screen and Keyboard inside Memory use the built-in chips of the simulator
(my RAM16K made from registers is too slow to simulate), all other chips are mine.

### Part B

```
python3 assembler.py asm_tests/Pong.asm
```

This makes `asm_tests/Pong.hack`. To compare my output with the official assembler output
(saved in `asm_tests/official/`):

```
python check_assembler.py    # on Windows / macOS / Linux
# or: bash check_assembler.sh
```

Upon assembly, the assembler displays the allocated symbol table mapping and code profiling metrics (K mod 3 = 0 feature):

```
OK: 47 instructions written to Box.hack
Assembly Analysis & Metrics (K mod 3 = 0 feature):
  Total Instructions : 47
  A-Instructions     : 23
  C-Instructions     : 24
Symbol Resolution Table & Memory Mapping:
  User Labels:
    (LOOP) -> ROM[0]
    (SETUP) -> ROM[8]
    (ROW) -> ROM[18]
    (WORD) -> ROM[26]
  User Variables:
    @color -> RAM[16]
    @addr -> RAM[17]
    @rows -> RAM[18]
    @ptr -> RAM[19]
    @cols -> RAM[20]
```

If there is an erroneous line in the .asm file, the assembler does not crash. It provides the exact line number:

```
Line 7: invalid instruction - unknown computation 'Q'
No .hack file was written.
```

### Part C

```
python3 assembler.py Box.asm
```

Then open the CPU Emulator, load `Box.hack`, select View -> Screen, run it and hold any key.
The box comes at rows 48 to 67 on the left side (width: 16 pixels / 1 word). When the key is released the box goes away.
