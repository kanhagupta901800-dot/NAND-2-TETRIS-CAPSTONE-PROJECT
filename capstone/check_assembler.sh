#!/usr/bin/env bash
# Compares the output of my assembler with the output of the official
# Nand2Tetris assembler (saved in asm_tests/official/).
# Run from the capstone folder:   bash check_assembler.sh

cd "$(dirname "$0")"
TMP=$(mktemp -d)

for p in Add Max Rect Pong Box; do
    if [ "$p" = "Box" ]; then src=Box.asm; else src=asm_tests/$p.asm; fi
    python3 assembler.py "$src" "$TMP/$p.hack" > /dev/null

    # compare line by line (ignores Windows line endings / last newline)
    if diff <(awk '{sub(/\r$/,""); print}' asm_tests/official/$p.hack) \
            <(awk '{sub(/\r$/,""); print}' "$TMP/$p.hack") > /dev/null; then
        echo "$p.asm -> same as official assembler ($(awk 'END{print NR}' "$TMP/$p.hack") lines)"
    else
        echo "$p.asm -> DIFFERENT from official assembler"
    fi
done

rm -rf "$TMP"
