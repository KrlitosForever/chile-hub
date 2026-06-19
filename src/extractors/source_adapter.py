"""Helpers reutilizables para extractores de fuente.

Proporciona funciones compartidas para extractores que siguen el patrón:
fetch remoto → snapshot raw → fallback a datos curados → normalizar →
metadata estándar → validar → escribir staging.

Úsalo solo en extractores candidatos o nuevos. Los extractores estables
con lógica de extracción compleja (subdere, bcentral, censo, RES) no
necesitan adaptarse a este módulo.
"""

import datetime
from pathlib import Path
from typing import Any

import requests

UTC = datetime.timezone.utc


def fetch_url_snapshot(
    url: str,
    raw_dir: Path,
    raw_prefix: str,
    timeout: int = 30,
) -> tuple[bool, bytes | None, str]:
    """Obtiene una URL y guarda el contenido crudo como snapshot con timestamp.

    Args:
        url: URL a descargar.
        raw_dir: Directorio donde guardar el snapshot (data/raw/).
        raw_prefix: Prefijo para el nombre del archivo crudo.
        timeout: Timeout HTTP en segundos.

    Returns:
        Tupla (success, content, note) donde:
        - success: True si la descarga y el guardado fueron exitosos.
        - content: Bytes crudos de la respuesta, o None si falló.
        - note: Nota descriptiva para incluir en los metadatos.
    """
    try:
        with requests.get(url, timeout=timeout) as response:
            response.raise_for_status()
            content = response.content
        stamp = datetime.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        raw_path = raw_dir / f"{raw_prefix}_{stamp}.html"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(content)
        return True, content, "official_landing_snapshot_saved"
    except Exception as exc:
        return False, None, f"official_landing_unavailable: {exc}"


def source_mode_from_live_success(success: bool) -> str:
    """Determina el source_mode según el éxito de la extracción live.

    Args:
        success: True si la fuente respondió correctamente.

    Returns:
        "live" si la extracción fue exitosa, "fallback" en caso contrario.
    """
    return "live" if success else "fallback"


def fallback_metadata_note(reason: str) -> str:
    """Genera una nota de metadata estandarizada para modo fallback.

    Args:
        reason: Motivo legible del uso de fallback.

    Returns:
        Nota con prefijo estandarizado.
    """
    return f"fallback_curated_rows_used: {reason}"


def build_standard_metadata(
    dataset: str,
    source_name: str,
    source_url: str,
    source_mode: str,
    source_detail: str,
    df: Any,
    notes: list[str],
    reuse_policy: dict,
) -> dict:
    """Construye el dict de metadata con los campos estándar del pipeline.

    Args:
        dataset: Nombre del dataset (ej. "finanzas_municipales").
        source_name: Nombre legible de la fuente.
        source_url: URL oficial de la fuente.
        source_mode: "live" o "fallback".
        source_detail: Clasificación detallada de la fuente.
        df: DataFrame de Polars con los datos normalizados.
        notes: Lista de notas operativas.
        reuse_policy: Dict con la política de reutilización.

    Returns:
        Dict de metadata listo para escribir en staging.
    """
    return {
        "dataset": dataset,
        "source_name": source_name,
        "source_url": source_url,
        "source_mode": source_mode,
        "source_detail": source_detail,
        "refreshed_at_utc": datetime.datetime.now(UTC).isoformat(),
        "record_count": df.height,
        "fields": df.columns,
        "notes": notes,
        "reuse_policy": reuse_policy,
    }
