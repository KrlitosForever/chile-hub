"""
Extractor de Indicadores Económicos de Referencia.

Fuente operativa : mindicador.cl (API pública de la comunidad)
Fuente original  : Banco Central de Chile (BCCh) e Instituto Nacional de
                   Estadísticas (INE). El BCCh permite libre reproducción
                   con citación de la fuente.

Estrategia de actualización:
  - Primera ejecución  : descarga el historial completo desde HISTORY_START_YEAR.
  - Ejecuciones sucesivas: actualización incremental del año en curso únicamente,
    preservando el historial ya descargado en staging.
"""

import os
import json
import time
import datetime
import requests
import polars as pl

# ── Rutas ─────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
RAW_DIR = os.path.join(DATA_DIR, "raw")
STAGING_DIR = os.path.join(DATA_DIR, "staging")
METADATA_PATH = os.path.join(STAGING_DIR, "indicadores.metadata.json")
STAGING_CSV_PATH = os.path.join(STAGING_DIR, "indicadores.csv")

# ── Configuración ─────────────────────────────────────────────────────────────
MINDICADOR_BASE = "https://mindicador.cl/api"
HISTORY_START_YEAR = 2010        # Año de inicio del historial
REQUEST_DELAY_SECONDS = 0.3      # Pausa entre llamadas para no saturar la API

# Indicadores a extraer en orden de prioridad
INDICATOR_CODES = ["uf", "dolar", "euro", "utm", "ipc"]

# Política de reutilización: los datos provienen del BCCh/INE (libre reproducción
# con citación). mindicador.cl es el agregador/punto de acceso, no la fuente original.
REUSE_POLICY = {
    "status": "open-attribution",
    "license": "Reproducción libre con citación (BCCh / INE)",
    "license_url": "https://www.bcentral.cl/web/banco-central/terminos-y-condiciones",
    "attribution_required": True,
    "redistribution_ok": True,
    "summary": (
        "Datos del Banco Central de Chile (BCCh) e INE. "
        "El BCCh permite libre reproducción con citación de la fuente. "
        "Acceso consolidado vía mindicador.cl (API pública de la comunidad)."
    ),
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def ensure_directories() -> None:
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(STAGING_DIR, exist_ok=True)


def write_metadata(metadata: dict) -> None:
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def save_raw_snapshot(payload: dict, codigo: str, year: int) -> None:
    """Persiste la respuesta cruda de la API para trazabilidad y auditoría."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"mindicador_{codigo}_{year}_{timestamp}.json"
    path = os.path.join(RAW_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ── Fetch ─────────────────────────────────────────────────────────────────────

def fetch_indicator_year(codigo: str, year: int) -> list:
    """
    Descarga todos los valores de un indicador para un año calendario.

    La API de mindicador.cl entrega datos diarios para UF, dólar y euro,
    y datos mensuales para UTM e IPC.

    Retorna una lista de dicts con claves: fecha, codigo_indicador, valor.
    """
    url = f"{MINDICADOR_BASE}/{codigo}/{year}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    payload = response.json()
    save_raw_snapshot(payload, codigo, year)

    records = []
    for item in payload.get("serie", []):
        raw_date = item.get("fecha", "")[:10]   # YYYY-MM-DD
        valor = item.get("valor")
        if raw_date and valor is not None:
            records.append({
                "fecha": raw_date,
                "codigo_indicador": codigo,
                "valor": float(valor),
            })
    return records


def load_existing_staging():
    """
    Lee el CSV de staging existente para la estrategia incremental.
    Retorna (DataFrame, año_mínimo_a_re-fetch) o (None, None) si no existe.
    """
    if not os.path.exists(STAGING_CSV_PATH):
        return None, None
    try:
        df = pl.read_csv(
            STAGING_CSV_PATH,
            schema_overrides={"fecha": pl.String},
        ).with_columns(pl.col("fecha").str.to_date("%Y-%m-%d"))
        return df, datetime.date.today().year
    except Exception as e:
        print(f"Advertencia: no se pudo leer el staging existente: {e}. Se hará fetch completo.")
        return None, None


def fetch_all_history():
    """
    Descarga el historial completo o incremental de indicadores.

    - Si no existe staging: descarga desde HISTORY_START_YEAR hasta hoy.
    - Si existe staging  : re-fetcha solo el año en curso para incluir valores recientes.

    Retorna un DataFrame ordenado y deduplicado, o None si la API falla.
    """
    existing_df, _ = load_existing_staging()
    current_year = datetime.date.today().year

    if existing_df is not None:
        years_to_fetch = [current_year]
        print(f"Staging encontrado — actualizando solo el año {current_year} (incremental).")
    else:
        years_to_fetch = list(range(HISTORY_START_YEAR, current_year + 1))
        print(f"Sin staging previo — descargando historial completo desde {HISTORY_START_YEAR}.")

    total_calls = len(INDICATOR_CODES) * len(years_to_fetch)
    call_n = 0
    new_records = []

    for codigo in INDICATOR_CODES:
        for year in years_to_fetch:
            call_n += 1
            print(f"  [{call_n}/{total_calls}] Descargando {codigo}/{year}…")
            try:
                records = fetch_indicator_year(codigo, year)
                new_records.extend(records)
            except Exception as e:
                print(f"  Advertencia: no se pudo obtener {codigo}/{year}: {e}")
            time.sleep(REQUEST_DELAY_SECONDS)

    if not new_records:
        print("Error: no se obtuvieron datos de mindicador.cl.")
        return None

    new_df = pl.DataFrame(new_records).with_columns(
        pl.col("fecha").str.to_date("%Y-%m-%d"),
        pl.col("codigo_indicador").cast(pl.String),
        pl.col("valor").cast(pl.Float64),
    )

    if existing_df is not None:
        # Eliminar el año re-fetcheado del staging previo, luego concatenar
        existing_trimmed = existing_df.filter(
            ~pl.col("fecha").dt.year().is_in(years_to_fetch)
        )
        combined_df = pl.concat([existing_trimmed, new_df], how="vertical")
    else:
        combined_df = new_df

    return (
        combined_df
        .unique(subset=["fecha", "codigo_indicador"], keep="last")
        .sort(["fecha", "codigo_indicador"])
    )


# ── Fallback ──────────────────────────────────────────────────────────────────

def generate_fallback_indicators() -> pl.DataFrame:
    """
    Dataset sintético usado cuando la API en vivo no está disponible.
    Cubre los últimos 7 días con valores aproximados del año 2026.
    Marcado explícitamente como fallback en los metadatos.
    """
    print("Generando dataset de indicadores de fallback (simulación offline)…")
    today = datetime.date.today()
    base_values = {
        "uf":     40500.00,
        "dolar":    900.00,
        "euro":    1040.00,
        "utm":    70000.00,
        "ipc":        0.2,
    }
    records = []
    for i in range(7):
        fecha = (today - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        for codigo, base in base_values.items():
            valor = round(base - i * 5.0, 2) if codigo in ("uf", "dolar", "euro") else base
            records.append({"fecha": fecha, "codigo_indicador": codigo, "valor": valor})

    return (
        pl.DataFrame(records)
        .with_columns(pl.col("fecha").str.to_date("%Y-%m-%d"))
        .sort(["fecha", "codigo_indicador"])
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def process_indicators() -> str:
    ensure_directories()
    source_mode = "live"
    notes: list = []

    df = fetch_all_history()

    if df is None:
        df = generate_fallback_indicators()
        source_mode = "fallback"
        notes.append("fallback_due_to_live_fetch_failure")

    df.write_csv(STAGING_CSV_PATH)

    metadata = {
        "dataset": "indicadores",
        "source_name": "Banco Central de Chile (via mindicador.cl)",
        "source_url": MINDICADOR_BASE,
        "source_origin_url": "https://www.bcentral.cl/web/banco-central/estadisticas",
        "source_mode": source_mode,
        "source_detail": "public_api" if source_mode == "live" else "generated_fallback",
        "refreshed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "record_count": df.height,
        "fields": df.columns,
        "indicator_codes": sorted(df["codigo_indicador"].unique().to_list()),
        "history_start_year": HISTORY_START_YEAR,
        "notes": notes,
        "reuse_policy": REUSE_POLICY,
    }
    write_metadata(metadata)

    print(
        f"Indicadores guardados en: {STAGING_CSV_PATH} "
        f"({df.height} registros, {source_mode})"
    )
    return STAGING_CSV_PATH


if __name__ == "__main__":
    process_indicators()
