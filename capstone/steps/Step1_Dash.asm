// Step 1 - one dash: paint ONE word (16 pixels) black at the start of row 48.
// Address = SCREEN + 32*48 = 16384 + 1536 = 17920
    @SCREEN
    D=A
    @1536
    D=D+A           // D = 17920
    @addr
    M=D             // addr = 17920
    A=D             // A = 17920
    M=-1            // RAM[17920] = -1  -> 16 black pixels
(END)
    @END
    0;JMP           // stop here forever
