import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
NORMALIZED_DIR = ROOT_DIR / "data" / "normalized"
PIPELINE_METADATA_PATH = NORMALIZED_DIR / "pipeline_metadata.json"
STATUS_MARKDOWN_PATH = NORMALIZED_DIR / "pipeline_status.md"
DATASET_CATALOG_MARKDOWN_PATH = NORMALIZED_DIR / "dataset_catalog.md"
HUB_HEALTH_MARKDOWN_PATH = NORMALIZED_DIR / "hub_health.md"


def load_metadata(path=PIPELINE_METADATA_PATH):
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def format_warnings(warnings):
    if not warnings:
        return "none"
    return "; ".join(warnings)


def format_freshness(freshness):
    if not freshness:
        return "unknown"
    status = freshness.get("status", "unknown")
    age_hours = freshness.get("age_hours")
    max_age_hours = freshness.get("max_age_hours")
    if age_hours is None or max_age_hours is None:
        return status
    return f"{status} ({age_hours}h / {max_age_hours}h)"


def build_hub_health(metadata):
    datasets = metadata.get("datasets", {})
    validations = metadata.get("validations", {})
    entries = []

    for dataset_name in sorted(datasets.keys()):
        dataset = datasets[dataset_name]
        validation = validations.get(dataset_name, {})
        warning_count = len(validation.get("warnings", []))
        freshness_status = dataset.get("freshness", {}).get("status", "unknown")
        source_mode = dataset.get("source_mode", "unknown")
        validation_status = validation.get("status", "unknown")

        severity = "ok"
        if validation_status != "ok":
            severity = "error"
        elif freshness_status in {"stale", "unknown"}:
            severity = "warn"
        elif source_mode == "fallback" or warning_count > 0:
            severity = "warn"

        entries.append(
            {
                "dataset": dataset_name,
                "severity": severity,
                "source_mode": source_mode,
                "freshness_status": freshness_status,
                "validation_status": validation_status,
                "warning_count": warning_count,
            }
        )

    error_count = sum(1 for entry in entries if entry["severity"] == "error")
    warn_count = sum(1 for entry in entries if entry["severity"] == "warn")
    ok_count = sum(1 for entry in entries if entry["severity"] == "ok")
    overall_status = "error" if error_count else "warn" if warn_count else "ok"

    return {
        "generated_at_utc": metadata.get("generated_at_utc"),
        "overall_status": overall_status,
        "dataset_count": len(entries),
        "ok_count": ok_count,
        "warn_count": warn_count,
        "error_count": error_count,
        "live_count": sum(1 for entry in entries if entry["source_mode"] == "live"),
        "fallback_count": sum(1 for entry in entries if entry["source_mode"] == "fallback"),
        "stale_count": sum(1 for entry in entries if entry["freshness_status"] == "stale"),
        "unknown_freshness_count": sum(
            1 for entry in entries if entry["freshness_status"] == "unknown"
        ),
        "warning_count": sum(entry["warning_count"] for entry in entries),
        "datasets": entries,
    }


def build_status_text(metadata):
    lines = []
    generated_at = metadata.get("generated_at_utc", "unknown")
    lines.append("chile-hub pipeline status")
    lines.append(f"generated_at_utc: {generated_at}")
    lines.append("")

    datasets = metadata.get("datasets", {})
    validations = metadata.get("validations", {})

    for dataset_name in sorted(datasets.keys()):
        dataset = datasets[dataset_name]
        validation = validations.get(dataset_name, {})

        lines.append(f"[{dataset_name}]")
        lines.append(f"source: {dataset.get('source_name', 'unknown')}")
        lines.append(f"mode: {dataset.get('source_mode', 'unknown')}")
        lines.append(f"detail: {dataset.get('source_detail', 'unknown')}")
        lines.append(f"refreshed_at_utc: {dataset.get('refreshed_at_utc', 'unknown')}")
        lines.append(f"freshness: {format_freshness(dataset.get('freshness'))}")
        lines.append(f"records: {dataset.get('record_count', 'unknown')}")
        lines.append(f"validation_status: {validation.get('status', 'unknown')}")
        lines.append(f"warnings: {format_warnings(validation.get('warnings', []))}")

        notes = dataset.get("notes", [])
        if notes:
            lines.append(f"notes: {'; '.join(notes)}")

        indicator_codes = dataset.get("indicator_codes")
        if indicator_codes:
            lines.append(f"indicator_codes: {', '.join(indicator_codes)}")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_status_markdown(metadata):
    generated_at = metadata.get("generated_at_utc", "unknown")
    datasets = metadata.get("datasets", {})
    validations = metadata.get("validations", {})

    lines = [
        "# chile-hub pipeline status",
        "",
        f"- `generated_at_utc`: `{generated_at}`",
        "",
        "| Dataset | Source | Mode | Detail | Freshness | Records | Validation | Warnings |",
        "| :--- | :--- | :--- | :--- | :--- | ---: | :--- | :--- |",
    ]

    for dataset_name in sorted(datasets.keys()):
        dataset = datasets[dataset_name]
        validation = validations.get(dataset_name, {})
        warnings = format_warnings(validation.get("warnings", []))
        lines.append(
            "| "
            f"`{dataset_name}` | "
            f"{dataset.get('source_name', 'unknown')} | "
            f"`{dataset.get('source_mode', 'unknown')}` | "
            f"`{dataset.get('source_detail', 'unknown')}` | "
            f"`{format_freshness(dataset.get('freshness'))}` | "
            f"{dataset.get('record_count', 'unknown')} | "
            f"`{validation.get('status', 'unknown')}` | "
            f"{warnings} |"
        )

    lines.append("")

    for dataset_name in sorted(datasets.keys()):
        dataset = datasets[dataset_name]
        validation = validations.get(dataset_name, {})
        lines.append(f"## {dataset_name}")
        lines.append("")
        lines.append(f"- `refreshed_at_utc`: `{dataset.get('refreshed_at_utc', 'unknown')}`")
        lines.append(f"- `freshness`: `{format_freshness(dataset.get('freshness'))}`")
        lines.append(f"- `fields`: `{', '.join(dataset.get('fields', []))}`")

        notes = dataset.get("notes", [])
        if notes:
            lines.append(f"- `notes`: {'; '.join(notes)}")

        indicator_codes = dataset.get("indicator_codes")
        if indicator_codes:
            lines.append(f"- `indicator_codes`: `{', '.join(indicator_codes)}`")

        warnings = validation.get("warnings", [])
        if warnings:
            lines.append(f"- `warnings`: {'; '.join(warnings)}")
        else:
            lines.append("- `warnings`: none")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_status_markdown_file(metadata, path=STATUS_MARKDOWN_PATH):
    Path(path).write_text(build_status_markdown(metadata), encoding="utf-8")


def build_hub_health_markdown(health):
    lines = [
        "# chile-hub health summary",
        "",
        f"- `generated_at_utc`: `{health.get('generated_at_utc', 'unknown')}`",
        f"- `overall_status`: `{health.get('overall_status', 'unknown')}`",
        f"- `dataset_count`: `{health.get('dataset_count', 0)}`",
        f"- `ok_count`: `{health.get('ok_count', 0)}`",
        f"- `warn_count`: `{health.get('warn_count', 0)}`",
        f"- `error_count`: `{health.get('error_count', 0)}`",
        f"- `live_count`: `{health.get('live_count', 0)}`",
        f"- `fallback_count`: `{health.get('fallback_count', 0)}`",
        f"- `stale_count`: `{health.get('stale_count', 0)}`",
        f"- `warning_count`: `{health.get('warning_count', 0)}`",
        "",
        "| Dataset | Severity | Mode | Freshness | Validation | Warnings |",
        "| :--- | :--- | :--- | :--- | :--- | ---: |",
    ]

    for entry in health.get("datasets", []):
        lines.append(
            "| "
            f"`{entry.get('dataset', 'unknown')}` | "
            f"`{entry.get('severity', 'unknown')}` | "
            f"`{entry.get('source_mode', 'unknown')}` | "
            f"`{entry.get('freshness_status', 'unknown')}` | "
            f"`{entry.get('validation_status', 'unknown')}` | "
            f"{entry.get('warning_count', 0)} |"
        )

    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_hub_health_markdown_file(health, path=HUB_HEALTH_MARKDOWN_PATH):
    Path(path).write_text(build_hub_health_markdown(health), encoding="utf-8")


def build_dataset_catalog_markdown(catalog):
    lines = [
        "# chile-hub dataset catalog",
        "",
        f"- `generated_at_utc`: `{catalog.get('generated_at_utc', 'unknown')}`",
        f"- `dataset_count`: `{catalog.get('dataset_count', 0)}`",
        "",
        "| Dataset | Source | Mode | Freshness | Records | Confidence | Join Keys | Validation |",
        "| :--- | :--- | :--- | :--- | ---: | :--- | :--- | :--- |",
    ]

    for entry in catalog.get("datasets", []):
        lines.append(
            "| "
            f"`{entry.get('dataset', 'unknown')}` | "
            f"{entry.get('source_name', 'unknown')} | "
            f"`{entry.get('source_mode', 'unknown')}` | "
            f"`{format_freshness(entry.get('freshness'))}` | "
            f"{entry.get('record_count', 'unknown')} | "
            f"`{entry.get('confidence_tier', 'unknown')}` | "
            f"`{', '.join(entry.get('join_keys', []))}` | "
            f"`{entry.get('validation_status', 'unknown')}` |"
        )

    lines.append("")

    for entry in catalog.get("datasets", []):
        lines.append(f"## {entry.get('dataset', 'unknown')}")
        lines.append("")
        lines.append(entry.get("description", ""))
        lines.append("")
        lines.append(f"- `source_url`: {entry.get('source_url', 'unknown')}")
        lines.append(f"- `documentation`: `{entry.get('documentation', 'unknown')}`")
        lines.append(f"- `freshness`: `{format_freshness(entry.get('freshness'))}`")
        lines.append(f"- `fields`: `{', '.join(entry.get('fields', []))}`")
        lines.append(f"- `join_keys`: `{', '.join(entry.get('join_keys', []))}`")
        lines.append(f"- `outputs`: `{json.dumps(entry.get('outputs', {}), ensure_ascii=False)}`")
        usage_examples = entry.get("usage_examples", {})
        if usage_examples:
            lines.append(f"- `usage_examples`: `{json.dumps(usage_examples, ensure_ascii=False)}`")

        warnings = entry.get("warnings", [])
        if warnings:
            lines.append(f"- `warnings`: {'; '.join(warnings)}")
        else:
            lines.append("- `warnings`: none")

        notes = entry.get("notes", [])
        if notes:
            lines.append(f"- `notes`: {'; '.join(notes)}")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_dataset_catalog_markdown_file(catalog, path=DATASET_CATALOG_MARKDOWN_PATH):
    Path(path).write_text(build_dataset_catalog_markdown(catalog), encoding="utf-8")
