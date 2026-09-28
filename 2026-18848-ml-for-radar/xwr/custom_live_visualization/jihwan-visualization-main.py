#!/usr/bin/env python3
"""Entry point for the AWR1843AOPEVM + DCA1000EVM live visualizer.

The implementation lives in the `radarviz` package next to this file; see
`radarviz/__init__.py` for the module map, the live panels and the keyboard
shortcuts, or run this script with `--help`.

    ./jihwan-visualization-main.py --simulate      # no hardware needed
    ./jihwan-visualization-main.py --selftest      # DSP checks only
    ./jihwan-visualization-main.py                 # live capture
"""

import os
import sys

# Importable no matter how the script is invoked (symlink, odd CWD, ...).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import main  # noqa: E402 - needs the path set above

if __name__ == "__main__":
    sys.exit(main())
