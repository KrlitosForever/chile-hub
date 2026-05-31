import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
STAGING_DIR = ROOT_DIR / "data" / "staging"
NORMALIZED_DIR = ROOT_DIR / "data" / "normalized"

REQUIRED_FILES = [
    STAGING_DIR / "comunas.csv",
    STAGING_DIR / "indicadores.csv",
    STAGING_DIR / "comunas.metadata.json",
    STAGING_DIR / "indicadores.metadata.json",
    NORMALIZED_DIR / "chile_data.duckdb",
    NORMALIZED_DIR / "chile_data.db",
    NORMALIZED_DIR / "chile_data_latest.xlsx",
    NORMALIZED_DIR / "regiones.parquet",
    NORMALIZED_DIR / "provincias.parquet",
    NORMALIZED_DIR / "comunas.parquet",
    NORMALIZED_DIR / "indicadores.parquet",
    NORMALIZED_DIR / "regiones.json",
    NORMALIZED_DIR / "provincias.json",
    NORMALIZED_DIR / "comunas.json",
    NORMALIZED_DIR / "indicadores_hoy.json",
    NORMALIZED_DIR / "pipeline_metadata.json",
    NORMALIZED_DIR / "pipeline_status.md",
    NORMALIZED_DIR / "hub_health.json",
    NORMALIZED_DIR / "hub_health.md",
    NORMALIZED_DIR / "hub_bundle.json",
    NORMALIZED_DIR / "redistribution_report.json",
    NORMALIZED_DIR / "redistribution_report.md",
    NORMALIZED_DIR / "provenance_report.json",
    NORMALIZED_DIR / "provenance_report.md",
    NORMALIZED_DIR / "dataset_catalog.json",
    NORMALIZED_DIR / "dataset_catalog.md",
    NORMALIZED_DIR / "artifact_manifest.json",
    NORMALIZED_DIR / "chile-hub-publishable-bundle.zip",
    NORMALIZED_DIR / "chile-hub-publishable-bundle.zip.sha256",
]

REQUIRED_DATASETS = {"regiones", "provincias", "comunas", "indicadores"}


def fail(message):
    print(f"ERROR: {message}")
    raise SystemExit(1)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def verify_required_files():
    missing = [str(path.relative_to(ROOT_DIR)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        fail(f"Missing required files: {', '.join(missing)}")


def verify_pipeline_metadata():
    metadata_path = NORMALIZED_DIR / "pipeline_metadata.json"
    metadata = load_json(metadata_path)

    datasets = metadata.get("datasets", {})
    validations = metadata.get("validations", {})
    missing_datasets = sorted(REQUIRED_DATASETS - set(datasets.keys()))
    missing_validations = sorted(REQUIRED_DATASETS - set(validations.keys()))

    if missing_datasets:
        fail(f"pipeline_metadata.json is missing dataset entries: {', '.join(missing_datasets)}")

    if missing_validations:
        fail(f"pipeline_metadata.json is missing validation entries: {', '.join(missing_validations)}")

    if not metadata.get("generated_at_utc"):
        fail("pipeline_metadata.json is missing generated_at_utc")

    warning_count = 0
    for dataset_name in sorted(REQUIRED_DATASETS):
        dataset_metadata = datasets[dataset_name]
        validation = validations[dataset_name]

        if dataset_metadata.get("dataset") != dataset_name:
            fail(f"Dataset metadata mismatch for {dataset_name}")

        if validation.get("dataset") != dataset_name:
            fail(f"Validation metadata mismatch for {dataset_name}")

        if not dataset_metadata.get("refreshed_at_utc"):
            fail(f"{dataset_name} metadata is missing refreshed_at_utc")

        if not dataset_metadata.get("fields"):
            fail(f"{dataset_name} metadata is missing fields")

        if dataset_metadata.get("source_mode") not in {"live", "fallback"}:
            fail(f"{dataset_name} metadata has invalid source_mode: {dataset_metadata.get('source_mode')}")

        freshness = dataset_metadata.get("freshness", {})
        if freshness.get("status") not in {"fresh", "stale", "unknown"}:
            fail(f"{dataset_name} metadata has invalid freshness status: {freshness.get('status')}")
        if freshness.get("max_age_hours") is None:
            fail(f"{dataset_name} metadata is missing freshness.max_age_hours")
        if not freshness.get("checked_at_utc"):
            fail(f"{dataset_name} metadata is missing freshness.checked_at_utc")

        if validation.get("status") != "ok":
            fail(f"{dataset_name} validation status is not ok: {validation.get('status')}")

        errors = validation.get("errors", [])
        if errors:
            fail(f"{dataset_name} validation contains errors: {errors}")

        if dataset_metadata.get("record_count") != validation.get("record_count"):
            fail(
                f"{dataset_name} record_count mismatch between datasets and validations: "
                f"{dataset_metadata.get('record_count')} vs {validation.get('record_count')}"
            )

        if validation.get("freshness_status") != freshness.get("status"):
            fail(
                f"{dataset_name} freshness mismatch between datasets and validations: "
                f"{freshness.get('status')} vs {validation.get('freshness_status')}"
            )

        warnings = validation.get("warnings", [])
        if freshness.get("status") in {"stale", "unknown"} and not warnings:
            fail(f"{dataset_name} should expose freshness warning when status is {freshness.get('status')}")
        if warnings:
            warning_count += len(warnings)
            for warning in warnings:
                print(f"WARNING [{dataset_name}]: {warning}")

        if dataset_name == "indicadores":
            expected_codes = ["dolar", "euro", "ipc", "uf", "utm"]
            if dataset_metadata.get("indicator_codes") != expected_codes:
                fail(
                    "indicadores metadata has unexpected indicator_codes: "
                    f"{dataset_metadata.get('indicator_codes')}"
                )
            if validation.get("indicator_codes") != expected_codes:
                fail(
                    "indicadores validation has unexpected indicator_codes: "
                    f"{validation.get('indicator_codes')}"
                )
        if dataset_name == "regiones" and validation.get("record_count") < 16:
            fail("regiones validation record_count looks too small")
        if dataset_name == "provincias" and validation.get("record_count") < 50:
            fail("provincias validation record_count looks too small")

    print(
        "Verification passed:"
        f" {len(REQUIRED_FILES)} required files found,"
        f" {len(REQUIRED_DATASETS)} datasets validated,"
        f" {warning_count} warnings."
    )


def verify_dataset_catalog():
    catalog_path = NORMALIZED_DIR / "dataset_catalog.json"
    catalog = load_json(catalog_path)

    if catalog.get("dataset_count") != len(REQUIRED_DATASETS):
        fail(
            "dataset_catalog.json has unexpected dataset_count: "
            f"{catalog.get('dataset_count')}"
        )

    datasets = catalog.get("datasets", [])
    dataset_names = {entry.get("dataset") for entry in datasets}
    if dataset_names != REQUIRED_DATASETS:
        fail(f"dataset_catalog.json has unexpected datasets: {sorted(dataset_names)}")

    for entry in datasets:
        if not entry.get("outputs"):
            fail(f"{entry.get('dataset')} catalog entry is missing outputs")
        if not entry.get("join_keys"):
            fail(f"{entry.get('dataset')} catalog entry is missing join_keys")
        reuse_policy = entry.get("reuse_policy", {})
        if reuse_policy.get("status") not in {"open-attribution", "public-api-review-terms"}:
            fail(
                f"{entry.get('dataset')} catalog entry has invalid reuse_policy.status: "
                f"{reuse_policy.get('status')}"
            )
        if not reuse_policy.get("license"):
            fail(f"{entry.get('dataset')} catalog entry is missing reuse_policy.license")
        if not reuse_policy.get("summary"):
            fail(f"{entry.get('dataset')} catalog entry is missing reuse_policy.summary")
        if reuse_policy.get("attribution_required") not in {True, False}:
            fail(
                f"{entry.get('dataset')} catalog entry has invalid reuse_policy.attribution_required"
            )
        if reuse_policy.get("redistribution_ok") not in {True, False}:
            fail(
                f"{entry.get('dataset')} catalog entry has invalid reuse_policy.redistribution_ok"
            )
        freshness = entry.get("freshness", {})
        if freshness.get("status") not in {"fresh", "stale", "unknown"}:
            fail(
                f"{entry.get('dataset')} catalog entry has invalid freshness.status: "
                f"{freshness.get('status')}"
            )
        if not entry.get("freshness_policy", {}).get("max_age_hours"):
            fail(f"{entry.get('dataset')} catalog entry is missing freshness_policy.max_age_hours")
        usage_examples = entry.get("usage_examples", {})
        for required_example in ("python", "duckdb", "cli"):
            if not usage_examples.get(required_example):
                fail(
                    f"{entry.get('dataset')} catalog entry is missing usage_examples.{required_example}"
                )
        if entry.get("validation_status") != "ok":
            fail(
                f"{entry.get('dataset')} catalog entry has invalid validation_status: "
                f"{entry.get('validation_status')}"
            )


def verify_artifact_manifest():
    manifest_path = NORMALIZED_DIR / "artifact_manifest.json"
    manifest = load_json(manifest_path)

    artifacts = manifest.get("artifacts", [])
    if manifest.get("artifact_count") != len(artifacts):
        fail(
            "artifact_manifest.json has inconsistent artifact_count: "
            f"{manifest.get('artifact_count')} vs {len(artifacts)}"
        )

    expected_paths = {
        "data/normalized/regiones.parquet",
        "data/normalized/provincias.parquet",
        "data/normalized/comunas.parquet",
        "data/normalized/indicadores.parquet",
        "data/normalized/regiones.json",
        "data/normalized/provincias.json",
        "data/normalized/comunas.json",
        "data/normalized/indicadores_hoy.json",
        "data/normalized/pipeline_metadata.json",
        "data/normalized/pipeline_status.md",
        "data/normalized/hub_health.json",
        "data/normalized/hub_health.md",
        "data/normalized/hub_bundle.json",
        "data/normalized/redistribution_report.json",
        "data/normalized/redistribution_report.md",
        "data/normalized/provenance_report.json",
        "data/normalized/provenance_report.md",
        "data/normalized/dataset_catalog.json",
        "data/normalized/dataset_catalog.md",
    }
    actual_paths = {entry.get("path") for entry in artifacts}
    if expected_paths - actual_paths:
        fail(
            "artifact_manifest.json is missing expected publishable files: "
            f"{sorted(expected_paths - actual_paths)}"
        )

    for entry in artifacts:
        path = entry.get("path")
        if path in expected_paths:
            if path.endswith((".parquet", ".json")) and path not in {
                "data/normalized/pipeline_metadata.json",
                "data/normalized/hub_health.json",
                "data/normalized/hub_bundle.json",
                "data/normalized/redistribution_report.json",
                "data/normalized/provenance_report.json",
                "data/normalized/dataset_catalog.json",
                "data/normalized/artifact_manifest.json",
            }:
                if not entry.get("dataset"):
                    fail(f"artifact manifest entry is missing dataset: {entry}")
            if path.endswith((".parquet", ".json")) and path not in {
                "data/normalized/pipeline_metadata.json",
                "data/normalized/hub_health.json",
                "data/normalized/hub_bundle.json",
                "data/normalized/redistribution_report.json",
                "data/normalized/provenance_report.json",
                "data/normalized/dataset_catalog.json",
                "data/normalized/artifact_manifest.json",
            }:
                if path.endswith(".parquet") and not entry.get("output_type") == "parquet":
                    fail(f"artifact manifest entry has invalid output_type for parquet: {entry}")
        if path in {
            "data/normalized/regiones.json",
            "data/normalized/provincias.json",
            "data/normalized/comunas.json",
            "data/normalized/indicadores_hoy.json",
        } and not entry.get("output_type") == "json":
            fail(f"artifact manifest entry has invalid output_type for json: {entry}")
        if not entry.get("sha256"):
            fail(f"artifact manifest entry is missing sha256: {entry}")
        if entry.get("size_bytes", 0) <= 0:
            fail(f"artifact manifest entry has invalid size_bytes: {entry}")

    packages = manifest.get("packages", [])
    if len(packages) != 1:
        fail(f"artifact_manifest.json has unexpected packages count: {len(packages)}")
    package = packages[0]
    if package.get("path") != "data/normalized/chile-hub-publishable-bundle.zip":
        fail(f"artifact_manifest.json has unexpected package path: {package}")
    if package.get("package_type") != "zip":
        fail(f"artifact_manifest.json has invalid package_type: {package}")
    if package.get("checksum_path") != "data/normalized/chile-hub-publishable-bundle.zip.sha256":
        fail(f"artifact_manifest.json has invalid checksum_path: {package}")
    if not package.get("sha256") or package.get("size_bytes", 0) <= 0:
        fail(f"artifact_manifest.json has invalid package metadata: {package}")


def verify_hub_health():
    health_path = NORMALIZED_DIR / "hub_health.json"
    health = load_json(health_path)

    if health.get("dataset_count") != len(REQUIRED_DATASETS):
        fail(f"hub_health.json has unexpected dataset_count: {health.get('dataset_count')}")

    if health.get("overall_status") not in {"ok", "warn", "error"}:
        fail(f"hub_health.json has invalid overall_status: {health.get('overall_status')}")
    for key in ("publishable_count", "review_terms_count", "unknown_reuse_count"):
        if health.get(key) is None:
            fail(f"hub_health.json is missing {key}")

    datasets = health.get("datasets", [])
    dataset_names = {entry.get("dataset") for entry in datasets}
    if dataset_names != REQUIRED_DATASETS:
        fail(f"hub_health.json has unexpected datasets: {sorted(dataset_names)}")

    for entry in datasets:
        if entry.get("severity") not in {"ok", "warn", "error"}:
            fail(f"hub_health.json entry has invalid severity: {entry}")
        if entry.get("source_mode") not in {"live", "fallback"}:
            fail(f"hub_health.json entry has invalid source_mode: {entry}")
        if entry.get("freshness_status") not in {"fresh", "stale", "unknown"}:
            fail(f"hub_health.json entry has invalid freshness_status: {entry}")
        if entry.get("validation_status") != "ok":
            fail(f"hub_health.json entry has unexpected validation_status: {entry}")
        if entry.get("publishability_status") not in {"ready", "review_terms", "unknown"}:
            fail(f"hub_health.json entry has invalid publishability_status: {entry}")


def verify_hub_bundle():
    bundle_path = NORMALIZED_DIR / "hub_bundle.json"
    bundle = load_json(bundle_path)

    if bundle.get("dataset_count") != len(REQUIRED_DATASETS):
        fail(f"hub_bundle.json has unexpected dataset_count: {bundle.get('dataset_count')}")
    if bundle.get("overall_status") not in {"ok", "warn", "error"}:
        fail(f"hub_bundle.json has invalid overall_status: {bundle.get('overall_status')}")

    datasets = bundle.get("datasets", [])
    dataset_names = {entry.get("dataset") for entry in datasets}
    if dataset_names != REQUIRED_DATASETS:
        fail(f"hub_bundle.json has unexpected datasets: {sorted(dataset_names)}")

    for entry in datasets:
        if not entry.get("artifacts"):
            fail(f"hub_bundle.json dataset entry is missing artifacts: {entry.get('dataset')}")
        if entry.get("severity") not in {"ok", "warn", "error"}:
            fail(f"hub_bundle.json dataset entry has invalid severity: {entry}")
        if entry.get("validation_status") != "ok":
            fail(f"hub_bundle.json dataset entry has unexpected validation_status: {entry}")
        reuse_policy = entry.get("reuse_policy", {})
        if reuse_policy.get("status") not in {"open-attribution", "public-api-review-terms"}:
            fail(f"hub_bundle.json dataset entry has invalid reuse_policy: {entry}")
        if entry.get("publishability_status") not in {"ready", "review_terms", "unknown"}:
            fail(f"hub_bundle.json dataset entry has invalid publishability_status: {entry}")
    packages = bundle.get("packages", [])
    if len(packages) != 1 or packages[0].get("package_type") != "zip":
        fail(f"hub_bundle.json has invalid packages metadata: {packages}")


def verify_redistribution_report():
    report_path = NORMALIZED_DIR / "redistribution_report.json"
    report = load_json(report_path)

    if report.get("dataset_count") != len(REQUIRED_DATASETS):
        fail(
            "redistribution_report.json has unexpected dataset_count: "
            f"{report.get('dataset_count')}"
        )
    datasets = report.get("datasets", [])
    dataset_names = {entry.get("dataset") for entry in datasets}
    if dataset_names != REQUIRED_DATASETS:
        fail(f"redistribution_report.json has unexpected datasets: {sorted(dataset_names)}")
    for entry in datasets:
        if entry.get("publishability_status") not in {"ready", "review_terms", "unknown"}:
            fail(f"redistribution_report.json has invalid publishability_status: {entry}")
        if not entry.get("license"):
            fail(f"redistribution_report.json is missing license: {entry}")
        if not entry.get("recommended_action"):
            fail(f"redistribution_report.json is missing recommended_action: {entry}")
    if report.get("ready_count") is None or report.get("review_terms_count") is None:
        fail("redistribution_report.json is missing aggregated counts")


def verify_provenance_report():
    report_path = NORMALIZED_DIR / "provenance_report.json"
    report = load_json(report_path)

    if report.get("dataset_count") != len(REQUIRED_DATASETS):
        fail(
            "provenance_report.json has unexpected dataset_count: "
            f"{report.get('dataset_count')}"
        )
    datasets = report.get("datasets", [])
    dataset_names = {entry.get("dataset") for entry in datasets}
    if dataset_names != REQUIRED_DATASETS:
        fail(f"provenance_report.json has unexpected datasets: {sorted(dataset_names)}")
    for entry in datasets:
        if entry.get("source_mode") not in {"live", "fallback"}:
            fail(f"provenance_report.json has invalid source_mode: {entry}")
        if not entry.get("source_name"):
            fail(f"provenance_report.json is missing source_name: {entry}")
        if not entry.get("source_url"):
            fail(f"provenance_report.json is missing source_url: {entry}")
        if not entry.get("refreshed_at_utc"):
            fail(f"provenance_report.json is missing refreshed_at_utc: {entry}")
        if entry.get("freshness_status") not in {"fresh", "stale", "unknown"}:
            fail(f"provenance_report.json has invalid freshness_status: {entry}")


def verify_publishable_zip():
    zip_path = NORMALIZED_DIR / "chile-hub-publishable-bundle.zip"
    if zip_path.stat().st_size <= 0:
        fail("publishable bundle zip is empty")
    checksum_path = NORMALIZED_DIR / "chile-hub-publishable-bundle.zip.sha256"
    checksum_line = checksum_path.read_text(encoding="utf-8").strip()
    if "data/normalized/chile-hub-publishable-bundle.zip" not in checksum_line:
        fail("publishable bundle checksum file has unexpected contents")


def main():
    verify_required_files()
    verify_pipeline_metadata()
    verify_hub_health()
    verify_hub_bundle()
    verify_redistribution_report()
    verify_provenance_report()
    verify_dataset_catalog()
    verify_artifact_manifest()
    verify_publishable_zip()


if __name__ == "__main__":
    main()
