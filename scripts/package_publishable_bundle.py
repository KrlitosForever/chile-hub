import json
import sys
import zipfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
NORMALIZED_DIR = ROOT_DIR / "data" / "normalized"
MANIFEST_PATH = NORMALIZED_DIR / "artifact_manifest.json"
OUTPUT_ZIP_PATH = NORMALIZED_DIR / "chile-hub-publishable-bundle.zip"


def load_manifest(path=MANIFEST_PATH):
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def build_zip(manifest, output_path=OUTPUT_ZIP_PATH):
    artifact_paths = [ROOT_DIR / entry["path"] for entry in manifest.get("artifacts", [])]
    missing = [str(path.relative_to(ROOT_DIR)) for path in artifact_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing publishable artifacts: {', '.join(missing)}")

    output_path = Path(output_path)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in artifact_paths:
            archive.write(path, arcname=str(path.relative_to(ROOT_DIR)))
    return output_path


def main():
    manifest = load_manifest()
    output_path = build_zip(manifest)
    size_bytes = output_path.stat().st_size
    print(
        json.dumps(
            {
                "zip_path": str(output_path.relative_to(ROOT_DIR)),
                "artifact_count": manifest.get("artifact_count", 0),
                "size_bytes": size_bytes,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}")
        sys.exit(1)
