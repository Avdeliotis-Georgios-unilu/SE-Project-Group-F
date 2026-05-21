from __future__ import annotations

import os
import sys

_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJ_ROOT = os.path.dirname(_FILE_DIR)
if _PROJ_ROOT not in sys.path:
    sys.path.insert(0, _PROJ_ROOT)

from game.engine import SmartRPSGame  # noqa: E402

if __name__ == "__main__":
    SmartRPSGame().run()
    sys.exit()
