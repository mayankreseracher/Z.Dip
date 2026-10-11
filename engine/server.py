"""
Z.Dip / Zytor Sovereign - Legacy Engine Launcher

Maintains backward-compatibility with previous deployment scripts
by delegating to the unified zdip package server.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from zdip.server import app, main

if __name__ == "__main__":
    main()
