#!/bin/bash

set -e
set -o pipefail

cd $(dirname "$0")

### Input FSM

FSM=test.fsm

### Python implementation

python3 -m rsk_fsm.compile "$FSM" Python >"test_fsm.py"

### C implementation

OUT=test_fsm.out
SOURCE=test_fsm.c
HEADER=test_fsm.h
MAIN=test.c
BIN=test-fsm

python3 -m rsk_fsm.compile "$FSM" C >"$OUT"
cat "$OUT" | awk "$(printf '{print >out}; /\/\* EOF \*\//{out="%s"}' "$SOURCE")" out="$HEADER" -
INCLUDE="$(printf '#include "%s"' "$HEADER")"
sed -i "1i $INCLUDE\n" "$SOURCE"
gcc -o "$BIN" "$MAIN" "$SOURCE"
echo "./$BIN" "$@"
"./$BIN" "$@"
rm "$BIN"
