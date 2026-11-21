// Step 2 - dash using loop: paint 1 word (16 pixels) of row 48 with a loop.
    @SCREEN
    D=A
    @1536
    D=D+A
    @ptr
    M=D             // ptr = 17920 (first word of row 48)
    @1
    D=A
    @cols
    M=D             // cols = 1 word to paint
(WORD)
    @ptr
    A=M
    M=-1            // RAM[ptr] = -1 (black)
    @ptr
    M=M+1           // ptr = ptr + 1
    @cols
    MD=M-1          // cols = cols - 1
    @WORD
    D;JGT           // repeat while cols > 0
(END)
    @END
    0;JMP
