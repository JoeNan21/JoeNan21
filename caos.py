#!/usr/bin/env python3
"""Top-level entry point for the CAOS CLI.

Usage:  python caos.py <command> ...
"""
from caos.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
