from typing import Any

import polars as pl

EXPECTED_INDICATOR_CODES = {"uf", "dolar", "euro", "utm", "ipc"}
FALLBACK_COMUNAS_COUNT = 18
EXPECTED_LIVE_COMUNAS_COUNT = 346


def _missing_columns(df: pl.DataFrame, columns: list[str]) -> list[str]:
    return [column for column in columns if column not in df.columns]


def _duplicate_count(df: pl.DataFrame, columns: list[str]) -> int:
    if df.height == 0:
        return 0
    return df.height - df.select(columns).unique().height


def _invalid_fixed_length_count(df: pl.DataFrame, column: str, length: int) -> int:
    return df.filter(pl.col(column).cast(pl.String).str.len_chars() != length).height


def _unknown_codes(df: pl.DataFrame, column: str, valid_codes: list[str] | None) -> list[str]:
    if valid_codes is None:
        return []
    return sorted(set(df[column].drop_nulls().cast(pl.String).to_list()) - set(valid_codes))


def _negative_numeric_count(df: pl.DataFrame, columns: list[str]) -> int:
    count = 0
    for column in columns:
        count += df.filter(pl.col(column).is_not_null() & (pl.col(column) < 0)).height
    return count


def _percentage_out_of_bounds_count(df: pl.DataFrame, columns: list[str]) -> int:
    count = 0
    for column in columns:
        count += df.filter(
            pl.col(column).is_not_null() & ((pl.col(column) < 0) | (pl.col(column) > 100))
        ).height
    return count


def validate_comunas(df_comunas: pl.DataFrame, metadata: dict[str, Any] | None) -> dict[str, Any]:
    errors = []
    warnings = []
    row_count = df_comunas.height
    duplicate_count = row_count - df_comunas["codigo_comuna"].n_unique()

    if duplicate_count > 0:
        errors.append(f"codigo_comuna must be unique, found {duplicate_count} duplicate rows")

    if (
        metadata
        and metadata.get("source_mode") == "live"
        and row_count < EXPECTED_LIVE_COMUNAS_COUNT
    ):
        errors.append(
            f"live comunas dataset looks incomplete: {row_count} rows, expected at least {EXPECTED_LIVE_COMUNAS_COUNT}"
        )

    if metadata and metadata.get("source_mode") == "fallback":
        if row_count != FALLBACK_COMUNAS_COUNT:
            warnings.append(
                f"fallback comunas expected about {FALLBACK_COMUNAS_COUNT} rows, found {row_count}"
            )
        warnings.append("comunas source_mode is fallback; coverage is limited by design")

    return {
        "dataset": "comunas",
        "status": "error" if errors else "ok",
        "record_count": row_count,
        "errors": errors,
        "warnings": warnings,
    }


def validate_regiones(df_regiones: pl.DataFrame) -> dict[str, Any]:
    errors = []
    if df_regiones.height == 0:
        errors.append("regiones dataset is empty")
    duplicate_count = df_regiones.height - df_regiones["codigo_region"].n_unique()
    if duplicate_count > 0:
        errors.append(f"codigo_region must be unique, found {duplicate_count} duplicate rows")
    return {
        "dataset": "regiones",
        "status": "error" if errors else "ok",
        "record_count": df_regiones.height,
        "errors": errors,
        "warnings": [],
    }


def validate_provincias(df_provincias: pl.DataFrame) -> dict[str, Any]:
    errors = []
    if df_provincias.height == 0:
        errors.append("provincias dataset is empty")
    keys = (df_provincias["codigo_region"] + "-" + df_provincias["codigo_provincia"]).n_unique()
    if keys != df_provincias.height:
        errors.append("codigo_region + codigo_provincia must be unique")
    return {
        "dataset": "provincias",
        "status": "error" if errors else "ok",
        "record_count": df_provincias.height,
        "errors": errors,
        "warnings": [],
    }


def validate_censo_comunal(
    df_censo: pl.DataFrame, metadata: dict[str, Any] | None
) -> dict[str, Any]:
    errors = []
    row_count = df_censo.height
    if row_count == 0:
        errors.append("censo_comunal dataset is empty")
    if row_count != 346:
        errors.append(f"censo_comunal expected 346 communes, found {row_count}")
    if row_count - df_censo["codigo_comuna"].n_unique() > 0:
        errors.append("codigo_comuna must be unique in censo_comunal")
    age_total = sum(
        df_censo[column]
        for column in (
            "poblacion_0_14",
            "poblacion_15_29",
            "poblacion_30_44",
            "poblacion_45_64",
            "poblacion_65_mas",
        )
    )
    if df_censo.filter(age_total != df_censo["poblacion_censada"]).height > 0:
        errors.append("age bands must sum to poblacion_censada")
    return {
        "dataset": "censo_comunal",
        "status": "error" if errors else "ok",
        "record_count": row_count,
        "errors": errors,
        "warnings": [],
    }


def validate_establecimientos_salud(
    df_salud: pl.DataFrame,
    metadata: dict[str, Any] | None,
    valid_commune_codes: list[str] | None = None,
) -> dict[str, Any]:
    errors = []
    row_count = df_salud.height
    if row_count == 0:
        errors.append("establecimientos_salud dataset is empty")
    if row_count - df_salud["codigo_establecimiento"].n_unique() > 0:
        errors.append("codigo_establecimiento must be unique")
    invalid_codes = df_salud.filter(pl.col("codigo_comuna").str.len_chars() != 5).height
    if invalid_codes:
        errors.append(f"found {invalid_codes} invalid codigo_comuna values")
    if valid_commune_codes is not None:
        unknown = set(df_salud["codigo_comuna"].drop_nulls().to_list()) - set(valid_commune_codes)
        if unknown:
            errors.append(
                f"health facilities reference unknown communes: {', '.join(sorted(unknown))}"
            )
    return {
        "dataset": "establecimientos_salud",
        "status": "error" if errors else "ok",
        "record_count": row_count,
        "errors": errors,
        "warnings": [],
    }


def validate_censo_hogares_viviendas(
    df: pl.DataFrame,
    metadata: dict[str, Any] | None,
    valid_commune_codes: list[str] | None = None,
) -> dict[str, Any]:
    errors = []
    if df.height != 346:
        errors.append(f"censo_hogares_viviendas expected 346 communes, found {df.height}")
    if df.height - df["codigo_comuna"].n_unique() > 0:
        errors.append("codigo_comuna must be unique in censo_hogares_viviendas")
    if valid_commune_codes is not None:
        unknown = set(df["codigo_comuna"].to_list()) - set(valid_commune_codes)
        if unknown:
            errors.append(f"censo_hogares_viviendas references unknown communes: {sorted(unknown)}")
    inconsistent = df.filter(
        pl.col("viviendas_particulares_ocupadas")
        + pl.col("viviendas_particulares_desocupadas")
        + pl.col("viviendas_colectivas")
        != pl.col("viviendas_censadas")
    ).height
    if inconsistent:
        errors.append(f"housing totals are inconsistent for {inconsistent} communes")
    return {
        "dataset": "censo_hogares_viviendas",
        "status": "error" if errors else "ok",
        "record_count": df.height,
        "errors": errors,
        "warnings": [],
    }


def validate_establecimientos_educacionales(
    df: pl.DataFrame,
    metadata: dict[str, Any] | None,
    valid_commune_codes: list[str] | None = None,
) -> dict[str, Any]:
    errors = []
    if df.height == 0:
        errors.append("establecimientos_educacionales dataset is empty")
    if df.height - df["rbd"].n_unique() > 0:
        errors.append("rbd must be unique")
    invalid = df.filter(pl.col("codigo_comuna").str.len_chars() != 5).height
    if invalid:
        errors.append(f"found {invalid} invalid codigo_comuna values")
    if valid_commune_codes is not None:
        unknown = set(df["codigo_comuna"].drop_nulls().to_list()) - set(valid_commune_codes)
        if unknown:
            errors.append(f"education facilities reference unknown communes: {sorted(unknown)}")
    return {
        "dataset": "establecimientos_educacionales",
        "status": "error" if errors else "ok",
        "record_count": df.height,
        "errors": errors,
        "warnings": [],
    }


def validate_indicadores(
    df_indicadores: pl.DataFrame, metadata: dict[str, Any] | None
) -> dict[str, Any]:
    errors = []
    warnings = []
    row_count = df_indicadores.height
    codes = set(df_indicadores["codigo_indicador"].unique().to_list())
    missing_codes = sorted(EXPECTED_INDICATOR_CODES - codes)

    if row_count == 0:
        errors.append("indicadores dataset is empty")

    if missing_codes:
        errors.append(f"missing expected indicator codes: {', '.join(missing_codes)}")

    if metadata and metadata.get("source_mode") == "fallback":
        warnings.append(
            "indicadores source_mode is fallback; values are synthetic development data"
        )
    if metadata and metadata.get("raw_recoveries"):
        warnings.append(
            "indicadores live refresh reused raw snapshots for: "
            + ", ".join(metadata["raw_recoveries"])
        )
    if metadata and metadata.get("preserved_existing_pairs"):
        warnings.append(
            "indicadores live refresh preserved previous staging rows for: "
            + ", ".join(metadata["preserved_existing_pairs"])
        )
    if metadata and metadata.get("empty_live_pairs"):
        warnings.append(
            "indicadores live refresh returned empty series for: "
            + ", ".join(metadata["empty_live_pairs"])
        )
    if metadata and metadata.get("published_backfills"):
        warnings.append(
            "indicadores live refresh reused last published artifact for missing codes: "
            + ", ".join(metadata["published_backfills"])
        )

    return {
        "dataset": "indicadores",
        "status": "error" if errors else "ok",
        "record_count": row_count,
        "errors": errors,
        "warnings": warnings,
        "indicator_codes": sorted(codes),
    }


def validate_distritos_electorales(
    df: pl.DataFrame,
    metadata: dict[str, Any] | None,
    valid_commune_codes: list[str] | None = None,
) -> dict[str, Any]:
    errors = []
    if df.height == 0:
        errors.append("distritos_electorales dataset is empty")
    if df.height != 346:
        errors.append(f"distritos_electorales expected 346 communes, found {df.height}")
    if df.height - df["codigo_comuna"].n_unique() > 0:
        errors.append("codigo_comuna must be unique in distritos_electorales")
    invalid = df.filter(pl.col("codigo_comuna").str.len_chars() != 5).height
    if invalid:
        errors.append(f"found {invalid} invalid codigo_comuna values")
    if valid_commune_codes is not None:
        unknown = set(df["codigo_comuna"].drop_nulls().to_list()) - set(valid_commune_codes)
        if unknown:
            errors.append(f"distritos_electorales references unknown communes: {sorted(unknown)}")
    return {
        "dataset": "distritos_electorales",
        "status": "error" if errors else "ok",
        "record_count": df.height,
        "errors": errors,
        "warnings": [],
    }


def validate_finanzas_municipales(
    df: pl.DataFrame,
    metadata: dict[str, Any] | None,
    valid_commune_codes: list[str] | None = None,
) -> dict[str, Any]:
    errors = []
    warnings = []
    required = [
        "anio",
        "codigo_comuna",
        "nombre_comuna",
        "ingresos_totales",
        "gastos_totales",
        "ingresos_propios_permanentes",
        "fondo_comun_municipal",
        "gasto_personal",
        "gasto_inversion",
    ]
    missing = _missing_columns(df, required)
    if missing:
        errors.append(f"finanzas_municipales missing columns: {', '.join(missing)}")
    if df.height == 0:
        errors.append("finanzas_municipales dataset is empty")
    if not missing:
        duplicates = _duplicate_count(df, ["anio", "codigo_comuna"])
        if duplicates:
            errors.append(f"anio + codigo_comuna must be unique, found {duplicates} duplicates")
        invalid = _invalid_fixed_length_count(df, "codigo_comuna", 5)
        if invalid:
            errors.append(f"found {invalid} invalid codigo_comuna values")
        unknown = _unknown_codes(df, "codigo_comuna", valid_commune_codes)
        if unknown:
            errors.append(f"finanzas_municipales references unknown communes: {unknown}")
        negative = _negative_numeric_count(
            df,
            [
                "ingresos_totales",
                "gastos_totales",
                "ingresos_propios_permanentes",
                "fondo_comun_municipal",
                "gasto_personal",
                "gasto_inversion",
            ],
        )
        if negative:
            errors.append(f"found {negative} negative municipal finance values")
    if metadata and metadata.get("source_mode") == "fallback":
        warnings.append("finanzas_municipales source_mode is fallback; review before publication")
    return {
        "dataset": "finanzas_municipales",
        "status": "error" if errors else "ok",
        "record_count": df.height,
        "errors": errors,
        "warnings": warnings,
    }


def validate_resultados_educacionales(
    df: pl.DataFrame,
    metadata: dict[str, Any] | None,
    valid_commune_codes: list[str] | None = None,
) -> dict[str, Any]:
    errors = []
    warnings = []
    required = [
        "anio",
        "codigo_comuna",
        "matricula_total",
        "asistencia_promedio",
        "tasa_aprobacion",
        "tasa_reprobacion",
        "tasa_retiro",
        "establecimientos_reportados",
    ]
    missing = _missing_columns(df, required)
    if missing:
        errors.append(f"resultados_educacionales missing columns: {', '.join(missing)}")
    if df.height == 0:
        errors.append("resultados_educacionales dataset is empty")
    if not missing:
        duplicates = _duplicate_count(df, ["anio", "codigo_comuna"])
        if duplicates:
            errors.append(f"anio + codigo_comuna must be unique, found {duplicates} duplicates")
        invalid = _invalid_fixed_length_count(df, "codigo_comuna", 5)
        if invalid:
            errors.append(f"found {invalid} invalid codigo_comuna values")
        unknown = _unknown_codes(df, "codigo_comuna", valid_commune_codes)
        if unknown:
            errors.append(f"resultados_educacionales references unknown communes: {unknown}")
        negative = _negative_numeric_count(df, ["matricula_total", "establecimientos_reportados"])
        if negative:
            errors.append(f"found {negative} negative education outcome counts")
        out_of_bounds = _percentage_out_of_bounds_count(
            df, ["asistencia_promedio", "tasa_aprobacion", "tasa_reprobacion", "tasa_retiro"]
        )
        if out_of_bounds:
            errors.append(f"found {out_of_bounds} percentage values outside 0-100")
    if metadata and metadata.get("source_mode") == "fallback":
        warnings.append(
            "resultados_educacionales source_mode is fallback; review before publication"
        )
    return {
        "dataset": "resultados_educacionales",
        "status": "error" if errors else "ok",
        "record_count": df.height,
        "errors": errors,
        "warnings": warnings,
    }


def validate_indicadores_urbanos_siedu(
    df: pl.DataFrame,
    metadata: dict[str, Any] | None,
    valid_commune_codes: list[str] | None = None,
) -> dict[str, Any]:
    errors = []
    warnings = []
    required = [
        "anio",
        "codigo_comuna",
        "codigo_indicador",
        "nombre_indicador",
        "categoria",
        "valor",
        "unidad",
        "fuente_original",
        "cobertura_tipo",
    ]
    missing = _missing_columns(df, required)
    if missing:
        errors.append(f"indicadores_urbanos_siedu missing columns: {', '.join(missing)}")
    if df.height == 0:
        errors.append("indicadores_urbanos_siedu dataset is empty")
    if not missing:
        duplicates = _duplicate_count(df, ["anio", "codigo_comuna", "codigo_indicador"])
        if duplicates:
            errors.append(
                "anio + codigo_comuna + codigo_indicador must be unique, "
                f"found {duplicates} duplicates"
            )
        invalid = _invalid_fixed_length_count(df, "codigo_comuna", 5)
        if invalid:
            errors.append(f"found {invalid} invalid codigo_comuna values")
        unknown = _unknown_codes(df, "codigo_comuna", valid_commune_codes)
        if unknown:
            errors.append(f"indicadores_urbanos_siedu references unknown communes: {unknown}")
        all_null = (
            df.group_by("codigo_indicador")
            .agg(pl.col("valor").is_not_null().sum().alias("non_null_values"))
            .filter(pl.col("non_null_values") == 0)
            .height
        )
        if all_null:
            errors.append(f"found {all_null} SIEDU indicators with all-null values")
    if metadata and metadata.get("coverage", {}).get("status") in {"partial_expected", "partial"}:
        warnings.append("indicadores_urbanos_siedu has intentionally partial urban coverage")
    if metadata and metadata.get("source_mode") == "fallback":
        warnings.append(
            "indicadores_urbanos_siedu source_mode is fallback; review before publication"
        )
    return {
        "dataset": "indicadores_urbanos_siedu",
        "status": "error" if errors else "ok",
        "record_count": df.height,
        "errors": errors,
        "warnings": warnings,
    }


def validate_perfil_territorial_comunal(
    df: pl.DataFrame,
    metadata: dict[str, Any] | None,
    valid_commune_codes: list[str] | None = None,
) -> dict[str, Any]:
    errors = []
    warnings = []
    if df.height != 346:
        errors.append(f"perfil_territorial_comunal expected 346 communes, found {df.height}")
    if df.height and df.height - df["codigo_comuna"].n_unique() > 0:
        errors.append("codigo_comuna must be unique in perfil_territorial_comunal")
    if df.height and _invalid_fixed_length_count(df, "codigo_comuna", 5):
        errors.append("perfil_territorial_comunal contains invalid codigo_comuna values")
    unknown = _unknown_codes(df, "codigo_comuna", valid_commune_codes)
    if unknown:
        errors.append(f"perfil_territorial_comunal references unknown communes: {unknown}")
    duplicated_columns = sorted({column for column in df.columns if df.columns.count(column) > 1})
    if duplicated_columns:
        errors.append(f"perfil_territorial_comunal has duplicate columns: {duplicated_columns}")
    if metadata and metadata.get("notes"):
        warnings.extend(
            note for note in metadata.get("notes", []) if "metric_unavailable" in str(note)
        )
    return {
        "dataset": "perfil_territorial_comunal",
        "status": "error" if errors else "ok",
        "record_count": df.height,
        "errors": errors,
        "warnings": warnings,
    }
