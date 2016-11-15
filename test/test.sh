#!/usr/bin/env bash
python test.py

PROCESS=( `ps aux | grep "python -m SimpleHTTPServer 8000" | awk '/ /{print $1}' | wc -w` )
if [[ $PROCESS != 2 ]]; then
  python -m SimpleHTTPServer 8000 > /dev/null 2>&1 &
  sleep 3
fi
open http://localhost:8000/

# don't forget when exit killall python
