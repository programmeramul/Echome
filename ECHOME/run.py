#!/usr/bin/env python3
"""Run ECHOME application."""

import os
import sys
from pathlib import Path

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("ECHOME_PORT", "7860"))
    host = os.getenv("ECHOME_HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=port)