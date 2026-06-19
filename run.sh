#!/bin/bash
# Wrapper na run.py — przygotowuje wszystko i uruchamia SmartVOD (macOS/Linux).
# Równoważne: python3 run.py
cd "$(dirname "$0")"
exec python3 run.py "$@"
