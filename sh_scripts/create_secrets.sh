#!/bin/sh
mkdir -p /secrets
head -c 256 /dev/urandom > /secrets/session_key.bin
