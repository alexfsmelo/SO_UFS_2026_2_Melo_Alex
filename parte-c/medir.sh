#!/bin/bash
CONFIG="${1:-padrao}"
QUERY="${2:-curta}"
LOGFILE="$(dirname "$0")/experimentos.csv"
MODEL="deepseek-r1:7b"

[ ! -f "$LOGFILE" ] && echo "config,query_size,inicio,ttft_s,total_ms,ram_mb,threads,obs" > "$LOGFILE"

PROMPT="${3:-O que e um sistema operacional? Responda em 2 frases.}"

INICIO=$(python3 -c "import time; print(int(time.time()*1000))")

RESP=$(curl -s http://localhost:11434/api/generate \
  -d "{\"model\":\"$MODEL\",\"prompt\":\"$PROMPT\",\"stream\":false}")

FIM=$(python3 -c "import time; print(int(time.time()*1000))")
TOTAL=$((FIM - INICIO))
RAM=$(free -m | awk '/Mem/{print $3}')
THREADS=$(ps -eLf | grep -cE "llama-server|streamlit|python3")
TTFT=$(echo "$RESP" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(round(d.get('eval_duration', 0) / 1e9, 2))
except:
    print('-')
" 2>/dev/null)

echo "$CONFIG,$QUERY,$(date -Iseconds),$TTFT,$TOTAL,$RAM,$THREADS,-" >> "$LOGFILE"
echo "config=$CONFIG | query=$QUERY | total=${TOTAL}ms | ttft=${TTFT}s | ram=${RAM}MB | threads=$THREADS"
