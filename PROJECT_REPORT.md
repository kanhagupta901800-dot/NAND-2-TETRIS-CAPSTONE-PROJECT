# Capstone Project Report
## Nand to Tetris – I (Course Code: ETCCNT301)
### Design, Implementation, and Verification of the Hack Computer, Two-Pass Assembler, and Interactive Graphics Program

---

**Student Name:** Krishna Gupta  
**Roll Number:** 2501350048  
**Degree & Branch:** B.Tech Computer Science & Engineering (B.Tech CSE)  
**Semester:** Semester III  
**Academic Year:** 2026–2027  
**Department:** Department of Computer Science & Engineering  
**Institution:** School of Engineering & Technology, K.R. Mangalam University  

---

## Executive Summary

This capstone project constitutes the cumulative capstone work for the course **Nand to Tetris – I (ETCCNT301)**. The objective is to design, implement, and rigorously verify a complete, general-purpose 16-bit computing platform from the ground up:
1. **Part A (Hardware Platform):** Constructing the core digital hardware platform including elementary logic gates, the 16-bit Arithmetic Logic Unit (ALU), memory systems (Registers, RAM, PC), the Central Processing Unit (CPU), memory-mapped I/O, and the top-level Computer architecture in Hardware Description Language (HDL).
2. **Part B (Software Toolchain):** Engineering a robust, two-pass Hack Assembler in Python that translates assembly language instructions (`.asm`) into binary machine code (`.hack`), incorporating symbol resolution, variable memory allocation, and specific architectural enhancements mandated by roll number derivation ($K \pmod 3 = 0$).
3. **Part C (Low-Level Systems Application):** Developing an interactive, event-driven assembly graphics program (`Box.asm`) that interfaces with memory-mapped screen and keyboard hardware, customized to roll-number-derived geometric and positional parameters ($K = 48$).

Every component has been verified using official Nand2Tetris test scripts (`.tst` / `.cmp`), official assembly benchmarks (`Add`, `Max`, `Rect`, `Pong`), and visual CPU emulation.

---

## 1. Roll-Number-Based Mathematical Derivations

The capstone assignment enforces individual accountability through parametric assignment formulas governed by the student's college roll number.

### 1.1 Parameter Determination
* **Full Roll Number:** `2501350048`
* **Base Parameter ($K$):** Last two digits of the roll number  
  $$\mathbf{K = 48}$$

### 1.2 Mathematical Derivations Table
| Assignment Parameter | Governing Formula | Computed Value | Description / Implementation Impact |
| :--- | :--- | :--- | :--- |
| **Roll Number Suffix ($K$)** | $\text{Roll Number} \pmod{100}$ | **$48$** | Primary seed value for vertical position and dimensions |
| **Modulo 4 Factor** | $K \pmod 4 = 48 \pmod 4$ | **$0$** | Dimension scaling factor |
| **Box Horizontal Width (Words)** | $(K \pmod 4) + 1 = 0 + 1$ | **$1$ word** | Each word corresponds to 16 consecutive horizontal pixels |
| **Box Horizontal Width (Pixels)** | $16 \times ((K \pmod 4) + 1) = 16 \times 1$ | **$16$ pixels** | Total pixel width of the drawn rectangle on the Hack display |
| **Box Vertical Height** | Standard specification | **$20$ rows** | Number of consecutive raster scan lines drawn |
| **Starting Vertical Row** | Row $K$ | **Row $48$** | Vertical coordinate (row 0 to 255) where the top edge begins |
| **Ending Vertical Row** | Row $K + 19$ | **Row $67$** | Vertical coordinate where the bottom edge terminates (48 to 67 inclusive = 20 rows) |
| **Screen Memory Row Stride** | $32 \text{ words/row} \times K$ | **$1536$ words** | Offset added to base screen address `SCREEN` ($16384$) |
| **First Word Base Address** | $\text{SCREEN} + 32 \times K = 16384 + 1536$ | **$\mathbf{17920}$** | Exact physical memory address in Hack RAM for the first pixel word |
| **Modulo 3 Factor** | $K \pmod 3 = 48 \pmod 3$ | **$0$** | Specifies the custom assembler functional extension |
| **Assembler Custom Feature** | Feature for $K \pmod 3 = 0$ | **Assembly Metrics & Symbol Mapping** | Assembler outputs detailed instruction metrics, symbol tables, and memory maps with syntax error tracking |

---

## 2. Part A: Hack Computer Hardware Architecture

The Hack computer is a 16-bit Von Neumann architecture with separate memory spaces for code (Instruction ROM) and data (Data RAM), interconnected via buses to the Central Processing Unit.

```
       +-------------------------------------------------------+
       |                    HACK COMPUTER                      |
       |                                                       |
       |   +---------------+              +----------------+   |
       |   |               |   AddressM   |                |   |
+----->|   |      CPU      |------------->|     MEMORY     |   |
Reset  |   |               |<-------------| (RAM16K, Screen|   |
       |   |               |    inM       |  and Keyboard) |   |
       |   +---------------+              +----------------+   |
       |       |        ^                     |        |       |
       |   pc  |        | instruction         |        |       |
       |       v        |                     v        v       |
       |   +---------------+               [Screen] [Keyboard] |
       |   |  ROM32K       |                                   |
       |   |  (Program)    |                                   |
       |   +---------------+                                   |
       +-------------------------------------------------------+
```

### 2.1 Arithmetic Logic Unit (`ALU.hdl`)
The ALU computes 18 fundamental functions based on six control inputs (`zx`, `nx`, `zy`, `ny`, `f`, `no`):
* Input handling: Zeroing and bitwise negation of $X$ and $Y$ inputs.
* Core functional logic: Evaluates either 16-bit addition ($X + Y$) using a ripple-carry 16-bit adder (`Add16.hdl`) or bitwise AND ($X \ \& \ Y$) using `And16.hdl`.
* Post-processing: Output negation and condition flag generation (`zr` for zero detection and `ng` for negative detection via the MSB `out[15]`).

### 2.2 Central Processing Unit (`CPU.hdl`)
The CPU decodes both A-instructions (MSB = `0`) and C-instructions (MSB = `1`):
* **Instruction Decoding:** Decodes opcode bit `instruction[15]`, ALU control bits `instruction[6..11]`, destination registers `instruction[3..5]`, and branch condition bits `instruction[0..2]`.
* **Register Management:** 
  - Register A: Stores memory addresses or 15-bit constants.
  - Register D: General-purpose 16-bit data accumulator.
* **Program Counter (`PC.hdl`):** Computes program flow. Conditional jumping evaluates ALU status flags `zr` and `ng` against jump control bits. If jump conditions are satisfied, `PC` loads address from Register A; otherwise, it increments by 1.

### 2.3 Memory Subsystem (`Memory.hdl`)
The Hack memory space occupies 32,768 16-bit registers divided into three regions:
1. **Data RAM (`0x0000` to `0x3FFF` / addresses 0 to 16383):** 16K words implemented via built-in RAM16K.
2. **Screen Memory Map (`0x4000` to `0x5FFF` / addresses 16384 to 24575):** 8K words mapped directly to the $512 \times 256$ raster display.
3. **Keyboard Register (`0x6000` / address 24576):** Single memory-mapped register reflecting the current 16-bit scan-code of the pressed key.

Address decoding is performed using a `DMux4Way` on bits `address[13..14]`.

---

## 3. Part B: The Hack Assembler (`assembler.py`)

The assembler is built as a complete software toolchain in Python, conforming to the Hack assembly specification and incorporating the assigned $K \pmod 3 = 0$ enhancement.

### 3.1 Two-Pass Assembly Pipeline
1. **Pass 0 (Cleaning & Preprocessing):**
   - Strips single-line comments (`//`) and whitespace.
   - Retains original source line indices for accurate syntax error tracking.
2. **Pass 1 (Symbol Resolution):**
   - Populates the symbol table with predefined symbols (`SP`, `LCL`, `ARG`, `THIS`, `THAT`, `SCREEN`, `KBD`, `R0`–`R15`).
   - Identifies label declarations `(LABEL)` and records their target ROM execution address without incrementing the ROM instruction pointer.
3. **Pass 2 (Binary Code Generation & Allocation):**
   - Translates A-instructions (`@symbol` or `@constant`): Resolves symbolic variables by dynamically allocating available RAM addresses beginning at `RAM[16]`, formatted as `0` followed by 15-bit binary.
   - Translates C-instructions (`dest=comp;jump`): Deconstructs syntax tokens into standard 7-bit computation field, 3-bit destination field, and 3-bit jump field, formatted as `111 + comp + dest + jump`.

### 3.2 Roll-Number Derived Feature ($K \pmod 3 = 0$)
Because $48 \pmod 3 = 0$, the assembler implements **Assembly Metrics & Code Profiling** combined with a full **Symbol Resolution Table and Memory Mapping Dump**. Upon successful assembly, it prints:
* Instruction breakdown (Total instructions, A-instruction count, C-instruction count).
* User-defined branch targets (ROM Addresses).
* User-defined variable allocations (RAM Addresses starting from address 16).
* Graceful, non-crashing syntax validation with line numbers (`AsmError`).

### 3.3 Assembler Test Suite Verification
The assembler was tested against official benchmark programs using `check_assembler.py`:
* `Add.asm` (6 instructions) $\rightarrow$ **PASS** (100% binary match with official output)
* `Max.asm` (16 instructions) $\rightarrow$ **PASS** (100% binary match with official output)
* `Rect.asm` (25 instructions) $\rightarrow$ **PASS** (100% binary match with official output)
* `Pong.asm` (27,483 instructions) $\rightarrow$ **PASS** (100% binary match with official output)
* `Box.asm` (47 instructions) $\rightarrow$ **PASS** (100% binary match with official output)

---

## 4. Part C: Interactive Box Application (`Box.asm`)

### 4.1 Specification and Behavioral Logic
The program monitors the memory-mapped keyboard register (`KBD` = 24576). When any key is pressed, it draws a solid black rectangle on the screen; when the key is released, the rectangle is cleared to white.

* **Target Row Range:** Rows $48$ through $67$ (20 rows).
* **Width:** $16$ pixels ($1$ word per row).
* **Base Physical Address:** $16384 + (32 \times 48) = \mathbf{17920}$.

### 4.2 Progressive Development Steps
The program was engineered systematically across three evolutionary steps:
1. **Step 1 (`Step1_Dash.asm`):** Draws a single 16-pixel horizontal segment at `RAM[17920] = -1`.
2. **Step 2 (`Step2_WideDash.asm`):** Introduces loop-based painting for the column word using dynamic address pointer arithmetic (`ptr = ptr + 1`).
3. **Step 3 (`Step3_Box.asm`):** Establishes nested loops (inner word loop and outer row loop) to draw the full $16 \times 20$ box without keyboard interaction.
4. **Final (`Box.asm`):** Integrates an event loop that polls `KBD`, sets `@color` to `-1` (black) or `0` (white), and redraws the designated box region.

### 4.3 Memory Allocation Map for `Box.asm`
| Variable / Label | Type | Location | Purpose |
| :--- | :--- | :--- | :--- |
| `LOOP` | Code Label | ROM[0] | Top-level polling loop |
| `SETUP` | Code Label | ROM[8] | Initialization of screen coordinates and counters |
| `ROW` | Code Label | ROM[18] | Outer loop beginning (row stride iteration) |
| `WORD` | Code Label | ROM[26] | Inner loop beginning (pixel column writing) |
| `color` | Variable | RAM[16] | Active drawing color (`0` = white, `-1` = black) |
| `addr` | Variable | RAM[17] | Physical memory address of the first word of the current row |
| `rows` | Variable | RAM[18] | Remaining rows counter ($20$ counting down to $0$) |
| `ptr` | Variable | RAM[19] | Pointer to the active screen memory word being written |
| `cols` | Variable | RAM[20] | Remaining columns counter in current row ($1$ down to $0$) |

---

## 5. Verification Results and Simulation Analysis

1. **Hardware Verification:** All chips (`ALU`, `CPU`, `Memory`, `Computer`) successfully executed all official test scripts (`CPU.tst`, `Memory.tst`, `ComputerAdd.tst`, `ComputerMax.tst`, `ComputerRect.tst`) with zero discrepancies compared against `.cmp` reference files.
2. **Assembler Output Verification:** The Python assembler produced bit-exact machine code identical to the official Nand2Tetris Java assembler across all 27,000+ instructions of `Pong.hack` and all test programs.
3. **CPU Emulation Execution:** Loaded `Box.hack` in the CPU Emulator. When a key is pressed, `RAM[24576]` receives the key scan-code, prompting `Box.asm` to draw the solid $16 \times 20$ black box spanning row 48 to 67. Upon key release, `RAM[24576]` reverts to 0, clearing the screen region.

---

## 6. Conclusion

This project successfully integrates all major concepts taught in **Nand to Tetris – I**:
- Digital combinational and sequential circuit design using hardware abstraction.
- Instruction set architecture (ISA) implementation and CPU pipelining/control logic.
- Systems programming and compiler/assembler engineering using Python.
- Low-level assembly language graphics and memory-mapped hardware control.

All deliverables have been customized, verified, and placed under version control in the student's project repository.

---

## Appendix: Complete Assembly Source Code (`Box.asm`)

```hack
// Box.asm  -  Capstone Part C
// Name: Krishna Gupta      Roll no.: 2501350048      K = 48
//
// While any key is pressed, a black box is shown; when released it disappears.
//
// Box for K = 48:
//   starts at row K = 48, is 20 rows tall       -> rows 48 .. 67
//   width = 16 * ((K mod 4) + 1) = 16 * 1 = 16 px -> 1 word per row, from the left edge
//
// Screen memory: row r starts at SCREEN + 32*r  (32 words per row, 16 pixels per word)
//   first row of the box: SCREEN + 32*48 = 16384 + 1536 = 17920
// Writing -1 (all 16 bits = 1) to a word makes its 16 pixels black, 0 makes them white.
//
// Variables (RAM 16 onwards, assigned by the assembler):
//   color - value to write: 0 = white, -1 = black
//   addr  - address of the first word of the current row
//   ptr   - address of the word being painted inside the row
//   rows  - rows still to paint (counts 20 down to 0)
//   cols  - words still to paint in this row (counts 1 down to 0)

(LOOP)
    // ---- 1. Read the keyboard and choose the colour ----
    @KBD
    D=M                 // D = key code (0 when nothing is pressed)
    @color
    M=0                 // assume white
    @SETUP
    D;JEQ               // no key  -> keep white
    @color
    M=-1                // key pressed -> black

(SETUP)
    // ---- 2. Point addr at the first word of row 48 ----
    @SCREEN
    D=A
    @1536               // 32 * 48   (offset for row 48)
    D=D+A
    @addr
    M=D                 // addr = 17920
    @20                 // box height in rows
    D=A
    @rows
    M=D                 // rows = 20

(ROW)
    // ---- 3. Paint one row: 1 word starting at addr ----
    @addr
    D=M
    @ptr
    M=D                 // ptr = addr
    @1                  // box width in words: (48 mod 4) + 1 = 1
    D=A
    @cols
    M=D                 // cols = 1

(WORD)
    @color
    D=M                 // D = colour
    @ptr
    A=M                 // A = address of the word to paint
    M=D                 // RAM[ptr] = colour  (16 pixels)
    @ptr
    M=M+1               // ptr = ptr + 1  (next word to the right)
    @cols
    MD=M-1              // cols = cols - 1
    @WORD
    D;JGT               // words left in this row? -> paint the next one

    // ---- 4. Go down one row (32 words) ----
    @32
    D=A
    @addr
    M=D+M               // addr = addr + 32
    @rows
    MD=M-1              // rows = rows - 1
    @ROW
    D;JGT               // rows left? -> paint the next row

    @LOOP
    0;JMP               // box finished: check the keyboard again, forever
```\n