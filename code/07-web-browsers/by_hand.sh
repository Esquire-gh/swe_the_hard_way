#!/bin/sh
# Speak HTTP by hand against the machine that holds the first website.
#
# Run it with: sh by_hand.sh

HOST=info.cern.ch

echo "=== a correct request ==="
printf 'GET / HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n' "$HOST" \
    | nc -w 5 "$HOST" 80

echo
echo "=== the same request with no Host header ==="
printf 'GET / HTTP/1.1\r\nConnection: close\r\n\r\n' \
    | nc -w 5 "$HOST" 80 | head -6

echo
echo "=== asking for something that is not there ==="
printf 'GET /nothing-here HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n' "$HOST" \
    | nc -w 5 "$HOST" 80 | head -6
