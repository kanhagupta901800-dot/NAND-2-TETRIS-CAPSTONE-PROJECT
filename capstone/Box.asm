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
