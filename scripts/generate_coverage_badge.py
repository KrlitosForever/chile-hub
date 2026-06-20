"""Genera coverage_badge.json para el badge de shields.io desde coverage.xml.

Lee el reporte XML de coverage.py (generado por pytest --cov --cov-report=xml)
y produce un JSON compatible con shields.io endpoint badge.

Uso: python scripts/generate_coverage_badge.py
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
COVERAGE_XML = ROOT_DIR / "coverage.xml"
BADGE_PATH = ROOT_DIR / "data" / "normalized" / "coverage_badge.json"


def parse_coverage_pct(xml_path: Path) -> float:
    """Extrae el porcentaje de cobertura de líneas desde coverage.xml."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    # coverage.py usa el atributo line-rate en <coverage>
    line_rate = float(root.attrib.get("line-rate", 0))
    return round(line_rate * 100, 1)


def build_badge(coverage_pct: float) -> dict:
    """Construye el payload JSON para el endpoint de shields.io."""
    if coverage_pct >= 80:
        color = "green"
    elif coverage_pct >= 50:
        color = "yellow"
    else:
        color = "red"

    return {
        "schemaVersion": 1,
        "label": "coverage",
        "message": f"{coverage_pct}%",
        "color": color,
        "namedLogo": "pytest",
        "cacheSeconds": 3600,
    }


def main() -> None:
    if not COVERAGE_XML.exists():
        print(f"ERROR: {COVERAGE_XML} no encontrado. Ejecuta 'make coverage' primero.")
        sys.exit(1)

    pct = parse_coverage_pct(COVERAGE_XML)
    badge = build_badge(pct)
    BADGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BADGE_PATH.write_text(json.dumps(badge, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Badge de cobertura generado: {BADGE_PATH} → {badge['message']} ({badge['color']})")


if __name__ == "__main__":
    main()
