#!/bin/bash
# Usage: ./rpc_call.sh <method> <params_json>
METHOD="$1"
PARAMS="$2"
RESP=$(curl -s -m 120 -X POST http://127.0.0.1:8765/rpc -H 'Content-Type: application/json' \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"$METHOD\",\"params\":$PARAMS,\"id\":1}")
echo "$RESP"
