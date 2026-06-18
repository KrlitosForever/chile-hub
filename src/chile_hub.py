"""Shim de compatibilidad para la ruta de importación pre-paquete `src.chile_hub`.

El código nuevo debe importar desde `chile_hub`:

    from chile_hub import ChileHub
"""

import sys
from pathlib import Path

_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from chile_hub import ChileHub, main

__all__ = ["ChileHub", "main"]


if __name__ == "__main__":
    main()
