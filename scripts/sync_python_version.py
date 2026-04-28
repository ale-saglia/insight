#!/usr/bin/env python3
"""Update .devcontainer/Dockerfile Python version ARG to match .python-version.

Exits with code 1 if the Dockerfile was modified — CI treats this as a drift signal
and fails the build, prompting the developer to commit the updated Dockerfile.
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
version = (root / ".python-version").read_text().strip()
dockerfile = root / ".devcontainer" / "Dockerfile"
original = dockerfile.read_text()
updated = re.sub(r"ARG PYTHON_VERSION=\S+", f"ARG PYTHON_VERSION={version}", original)

if updated == original:
    print(f"Dockerfile already on PYTHON_VERSION={version}")
else:
    dockerfile.write_text(updated)
    print(f"Dockerfile updated to PYTHON_VERSION={version} — commit the change")
    sys.exit(1)
