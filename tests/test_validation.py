"""Tests unitarios para las funciones de validación en src/validation.py.

Cada validador se prueba con casos mínimos: datos correctos, errores
esperados y condiciones de borde.  Estos tests complementan los tests
de integración en test_chile_hub.py y test_pipeline_logic.py.
"""

import unittest

import polars as pl

from src.validation import (
    validate_censo_comunal,
    validate_censo_hogares_viviendas,
    validate_comunas,
    validate_distritos_electorales,
    validate_establecimientos_educacionales,
    validate_establecimientos_salud,
    validate_indicadores,
    validate_provincias,
    validate_regiones,
)

# ── Fixtures mínimos ──────────────────────────────────────────────────────────

VALID_COMMUNE_CODES = [f"{i:05d}" for i in range(1, 347)]  # "00001".."00346"


def _make_comunas_df(rows, *, source_mode="live"):
    """DataFrame mínimo de comunas con las columnas que espera el validador."""
    return pl.DataFrame(
        rows,
        schema={
            "codigo_comuna": pl.String,
            "codigo_region": pl.String,
            "codigo_provincia": pl.String,
            "nombre_comuna": pl.String,
        },
    )


# ── validate_regiones ─────────────────────────────────────────────────────────


class ValidateRegionesTests(unittest.TestCase):
    def test_ok_minimal(self):
        df = pl.DataFrame({"codigo_region": ["01", "02", "03"]})
        result = validate_regiones(df)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["record_count"], 3)

    def test_empty_dataset_is_error(self):
        df = pl.DataFrame({"codigo_region": []}, schema={"codigo_region": pl.String})
        result = validate_regiones(df)
        self.assertEqual(result["status"], "error")
        self.assertIn("empty", result["errors"][0])

    def test_duplicate_codes_error(self):
        df = pl.DataFrame({"codigo_region": ["01", "01", "02"]})
        result = validate_regiones(df)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("duplicate" in e for e in result["errors"]))


# ── validate_provincias ───────────────────────────────────────────────────────


class ValidateProvinciasTests(unittest.TestCase):
    def test_ok_minimal(self):
        df = pl.DataFrame(
            {
                "codigo_region": ["01", "01"],
                "codigo_provincia": ["011", "012"],
            }
        )
        result = validate_provincias(df)
        self.assertEqual(result["status"], "ok")

    def test_empty_dataset_is_error(self):
        df = pl.DataFrame(
            {"codigo_region": [], "codigo_provincia": []},
            schema={"codigo_region": pl.String, "codigo_provincia": pl.String},
        )
        result = validate_provincias(df)
        self.assertEqual(result["status"], "error")

    def test_duplicate_region_province_pair_error(self):
        df = pl.DataFrame(
            {
                "codigo_region": ["01", "01"],
                "codigo_provincia": ["011", "011"],
            }
        )
        result = validate_provincias(df)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("unique" in e for e in result["errors"]))


# ── validate_comunas ──────────────────────────────────────────────────────────


class ValidateComunasTests(unittest.TestCase):
    def test_ok_live_with_346_communes(self):
        rows = [
            {
                "codigo_comuna": f"{i:05d}",
                "codigo_region": f"{i // 10000:02d}",
                "codigo_provincia": f"{i // 1000:03d}",
                "nombre_comuna": f"Comuna {i}",
            }
            for i in range(1, 347)
        ]
        df = _make_comunas_df(rows, source_mode="live")
        result = validate_comunas(df, {"source_mode": "live"})
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["record_count"], 346)

    def test_duplicate_comuna_code_error(self):
        df = _make_comunas_df(
            [
                {
                    "codigo_comuna": "01101",
                    "codigo_region": "01",
                    "codigo_provincia": "011",
                    "nombre_comuna": "Iquique",
                },
                {
                    "codigo_comuna": "01101",
                    "codigo_region": "01",
                    "codigo_provincia": "011",
                    "nombre_comuna": "Duplicada",
                },
            ]
        )
        result = validate_comunas(df, None)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("duplicate" in e for e in result["errors"]))

    def test_live_mode_with_too_few_rows_error(self):
        df = _make_comunas_df(
            [
                {
                    "codigo_comuna": "01101",
                    "codigo_region": "01",
                    "codigo_provincia": "011",
                    "nombre_comuna": "Sola",
                }
            ],
            source_mode="live",
        )
        result = validate_comunas(df, {"source_mode": "live"})
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("incomplete" in e for e in result["errors"]))

    def test_fallback_mode_warns_on_unexpected_row_count(self):
        rows = [
            {
                "codigo_comuna": f"{i:05d}",
                "codigo_region": "01",
                "codigo_provincia": "011",
                "nombre_comuna": f"C{i}",
            }
            for i in range(1, 50)
        ]
        df = _make_comunas_df(rows)
        result = validate_comunas(df, {"source_mode": "fallback"})
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["warnings"])

    def test_fallback_mode_adds_coverage_warning(self):
        rows = [
            {
                "codigo_comuna": f"{i:05d}",
                "codigo_region": "01",
                "codigo_provincia": "011",
                "nombre_comuna": f"FB{i}",
            }
            for i in range(1, 19)  # Exactly FALLBACK_COMUNAS_COUNT (18)
        ]
        df = _make_comunas_df(rows)
        result = validate_comunas(df, {"source_mode": "fallback"})
        self.assertEqual(result["status"], "ok")
        self.assertTrue(any("limited" in w for w in result["warnings"]))


# ── validate_censo_comunal ────────────────────────────────────────────────────


class ValidateCensoComunalTests(unittest.TestCase):
    def _make_censo(self, rows):
        schema = {
            "codigo_comuna": pl.String,
            "poblacion_censada": pl.Int64,
            "poblacion_0_14": pl.Int64,
            "poblacion_15_29": pl.Int64,
            "poblacion_30_44": pl.Int64,
            "poblacion_45_64": pl.Int64,
            "poblacion_65_mas": pl.Int64,
        }
        return pl.DataFrame(rows, schema=schema)

    def test_ok_for_346_communes(self):
        rows = [
            {
                "codigo_comuna": f"{i:05d}",
                "poblacion_censada": 1000,
                "poblacion_0_14": 200,
                "poblacion_15_29": 200,
                "poblacion_30_44": 200,
                "poblacion_45_64": 200,
                "poblacion_65_mas": 200,
            }
            for i in range(1, 347)
        ]
        df = self._make_censo(rows)
        result = validate_censo_comunal(df, None)
        self.assertEqual(result["status"], "ok")

    def test_empty_dataset_error(self):
        df = pl.DataFrame(
            {
                "codigo_comuna": [],
                "poblacion_censada": [],
                "poblacion_0_14": [],
                "poblacion_15_29": [],
                "poblacion_30_44": [],
                "poblacion_45_64": [],
                "poblacion_65_mas": [],
            },
            schema={
                "codigo_comuna": pl.String,
                "poblacion_censada": pl.Int64,
                "poblacion_0_14": pl.Int64,
                "poblacion_15_29": pl.Int64,
                "poblacion_30_44": pl.Int64,
                "poblacion_45_64": pl.Int64,
                "poblacion_65_mas": pl.Int64,
            },
        )
        result = validate_censo_comunal(df, None)
        self.assertEqual(result["status"], "error")

    def test_wrong_row_count_error(self):
        df = self._make_censo(
            [
                {
                    "codigo_comuna": "01101",
                    "poblacion_censada": 100,
                    "poblacion_0_14": 50,
                    "poblacion_15_29": 50,
                    "poblacion_30_44": 0,
                    "poblacion_45_64": 0,
                    "poblacion_65_mas": 0,
                }
            ]
        )
        result = validate_censo_comunal(df, None)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("346" in e for e in result["errors"]))

    def test_duplicate_comuna_code_error(self):
        rows = [
            {
                "codigo_comuna": "01101",
                "poblacion_censada": 100,
                "poblacion_0_14": 50,
                "poblacion_15_29": 50,
                "poblacion_30_44": 0,
                "poblacion_45_64": 0,
                "poblacion_65_mas": 0,
            },
        ] * 346
        df = self._make_censo(rows)
        result = validate_censo_comunal(df, None)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("unique" in e for e in result["errors"]))

    def test_age_bands_must_sum_to_total(self):
        df = self._make_censo(
            [
                {
                    "codigo_comuna": f"{i:05d}",
                    "poblacion_censada": 1000,
                    "poblacion_0_14": 100,
                    "poblacion_15_29": 100,
                    "poblacion_30_44": 100,
                    "poblacion_45_64": 100,
                    "poblacion_65_mas": 100,  # suma 500 ≠ 1000
                }
                for i in range(1, 347)
            ]
        )
        result = validate_censo_comunal(df, None)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("sum" in e for e in result["errors"]))


# ── validate_censo_hogares_viviendas ──────────────────────────────────────────


class ValidateCensoHogaresViviendasTests(unittest.TestCase):
    def _make_df(self, rows):
        schema = {
            "codigo_comuna": pl.String,
            "viviendas_censadas": pl.Int64,
            "viviendas_particulares_ocupadas": pl.Int64,
            "viviendas_particulares_desocupadas": pl.Int64,
            "viviendas_colectivas": pl.Int64,
            "hogares_censados": pl.Int64,
        }
        return pl.DataFrame(rows, schema=schema)

    def test_ok_for_346_communes(self):
        rows = [
            {
                "codigo_comuna": f"{i:05d}",
                "viviendas_censadas": 60,
                "viviendas_particulares_ocupadas": 40,
                "viviendas_particulares_desocupadas": 15,
                "viviendas_colectivas": 5,
                "hogares_censados": 40,
            }
            for i in range(1, 347)
        ]
        df = self._make_df(rows)
        result = validate_censo_hogares_viviendas(df, None)
        self.assertEqual(result["status"], "ok")

    def test_inconsistent_housing_totals_error(self):
        rows = [
            {
                "codigo_comuna": f"{i:05d}",
                "viviendas_censadas": 100,
                "viviendas_particulares_ocupadas": 10,
                "viviendas_particulares_desocupadas": 10,
                "viviendas_colectivas": 10,  # suma 30 ≠ 100
                "hogares_censados": 10,
            }
            for i in range(1, 347)
        ]
        df = self._make_df(rows)
        result = validate_censo_hogares_viviendas(df, None)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("inconsistent" in e for e in result["errors"]))


# ── validate_indicadores ──────────────────────────────────────────────────────


class ValidateIndicadoresTests(unittest.TestCase):
    def test_ok_with_all_expected_codes(self):
        df = pl.DataFrame(
            {
                "codigo_indicador": ["uf", "dolar", "euro", "utm", "ipc"],
                "fecha": ["2024-01-01"] * 5,
                "valor": [1.0, 2.0, 3.0, 4.0, 5.0],
            }
        )
        result = validate_indicadores(df, None)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["indicator_codes"], ["dolar", "euro", "ipc", "uf", "utm"])

    def test_missing_indicator_codes_error(self):
        df = pl.DataFrame(
            {
                "codigo_indicador": ["uf", "dolar"],
                "fecha": ["2024-01-01"] * 2,
                "valor": [1.0, 2.0],
            }
        )
        result = validate_indicadores(df, None)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("missing" in e for e in result["errors"]))

    def test_empty_dataset_error(self):
        df = pl.DataFrame(
            {"codigo_indicador": [], "fecha": [], "valor": []},
            schema={
                "codigo_indicador": pl.String,
                "fecha": pl.String,
                "valor": pl.Float64,
            },
        )
        result = validate_indicadores(df, None)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("empty" in e for e in result["errors"]))

    def test_fallback_mode_adds_warning(self):
        df = pl.DataFrame(
            {
                "codigo_indicador": ["uf", "dolar", "euro", "utm", "ipc"],
                "fecha": ["2024-01-01"] * 5,
                "valor": [1.0, 2.0, 3.0, 4.0, 5.0],
            }
        )
        result = validate_indicadores(df, {"source_mode": "fallback"})
        self.assertEqual(result["status"], "ok")
        self.assertTrue(any("synthetic" in w for w in result["warnings"]))


# ── validate_distritos_electorales ─────────────────────────────────────────────


class ValidateDistritosElectoralesTests(unittest.TestCase):
    def _make_df(self, rows):
        schema = {
            "codigo_comuna": pl.String,
            "distrito_electoral": pl.String,
            "circunscripcion_senatorial": pl.String,
        }
        return pl.DataFrame(rows, schema=schema)

    def test_ok_for_346_communes(self):
        rows = [
            {
                "codigo_comuna": f"{i:05d}",
                "distrito_electoral": "10",
                "circunscripcion_senatorial": "5",
            }
            for i in range(1, 347)
        ]
        df = self._make_df(rows)
        result = validate_distritos_electorales(df, None)
        self.assertEqual(result["status"], "ok")

    def test_empty_dataset_error(self):
        df = pl.DataFrame(
            {
                "codigo_comuna": [],
                "distrito_electoral": [],
                "circunscripcion_senatorial": [],
            },
            schema={
                "codigo_comuna": pl.String,
                "distrito_electoral": pl.String,
                "circunscripcion_senatorial": pl.String,
            },
        )
        result = validate_distritos_electorales(df, None)
        self.assertEqual(result["status"], "error")

    def test_invalid_codigo_comuna_length_error(self):
        rows = [
            {
                "codigo_comuna": "123",  # solo 3 caracteres
                "distrito_electoral": "10",
                "circunscripcion_senatorial": "5",
            }
            for i in range(346)
        ]
        df = self._make_df(rows)
        result = validate_distritos_electorales(df, None)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("invalid" in e for e in result["errors"]))


# ── validate_establecimientos_salud ───────────────────────────────────────────


class ValidateEstablecimientosSaludTests(unittest.TestCase):
    def test_ok_minimal(self):
        df = pl.DataFrame(
            {
                "codigo_establecimiento": ["101", "102"],
                "codigo_comuna": ["01101", "01107"],
                "nombre_establecimiento": ["Hospital A", "CESFAM B"],
            }
        )
        result = validate_establecimientos_salud(df, None)
        self.assertEqual(result["status"], "ok")

    def test_empty_dataset_error(self):
        df = pl.DataFrame(
            {
                "codigo_establecimiento": [],
                "codigo_comuna": [],
                "nombre_establecimiento": [],
            },
            schema={
                "codigo_establecimiento": pl.String,
                "codigo_comuna": pl.String,
                "nombre_establecimiento": pl.String,
            },
        )
        result = validate_establecimientos_salud(df, None)
        self.assertEqual(result["status"], "error")

    def test_duplicate_codigo_establecimiento_error(self):
        df = pl.DataFrame(
            {
                "codigo_establecimiento": ["101", "101"],
                "codigo_comuna": ["01101", "01107"],
                "nombre_establecimiento": ["Hospital A", "CESFAM B"],
            }
        )
        result = validate_establecimientos_salud(df, None)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("unique" in e for e in result["errors"]))

    def test_invalid_comuna_code_length_error(self):
        df = pl.DataFrame(
            {
                "codigo_establecimiento": ["101"],
                "codigo_comuna": ["123456"],  # demasiado largo
                "nombre_establecimiento": ["Hospital A"],
            }
        )
        result = validate_establecimientos_salud(df, None)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("codigo_comuna" in e for e in result["errors"]))

    def test_unknown_comuna_codes_when_valid_list_provided(self):
        df = pl.DataFrame(
            {
                "codigo_establecimiento": ["101"],
                "codigo_comuna": ["99999"],
                "nombre_establecimiento": ["Hospital X"],
            }
        )
        result = validate_establecimientos_salud(df, None, valid_commune_codes=["01101"])
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("unknown" in e for e in result["errors"]))


# ── validate_establecimientos_educacionales ───────────────────────────────────


class ValidateEstablecimientosEducacionalesTests(unittest.TestCase):
    def test_ok_minimal(self):
        df = pl.DataFrame(
            {
                "rbd": ["1", "2"],
                "codigo_comuna": ["01101", "01107"],
                "nombre_establecimiento": ["Liceo A", "Escuela B"],
            }
        )
        result = validate_establecimientos_educacionales(df, None)
        self.assertEqual(result["status"], "ok")

    def test_empty_dataset_error(self):
        df = pl.DataFrame(
            {"rbd": [], "codigo_comuna": [], "nombre_establecimiento": []},
            schema={
                "rbd": pl.String,
                "codigo_comuna": pl.String,
                "nombre_establecimiento": pl.String,
            },
        )
        result = validate_establecimientos_educacionales(df, None)
        self.assertEqual(result["status"], "error")

    def test_duplicate_rbd_error(self):
        df = pl.DataFrame(
            {
                "rbd": ["1", "1"],
                "codigo_comuna": ["01101", "01107"],
                "nombre_establecimiento": ["Liceo A", "Escuela B"],
            }
        )
        result = validate_establecimientos_educacionales(df, None)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("unique" in e for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()
