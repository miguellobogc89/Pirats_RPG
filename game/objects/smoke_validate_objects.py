import json
from pathlib import Path

from game.objects.object_normalizer import normalize_object_definition
from game.objects.object_validator import validate_object_definition


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OBJECTS_DIR = PROJECT_ROOT / "data" / "objects"


def load_object_files():
    if not OBJECTS_DIR.exists():
        return []

    return sorted(OBJECTS_DIR.glob("*.json"))


def run_smoke():
    object_paths = load_object_files()
    total_errors = 0
    total_warnings = 0
    normalized_counts = {}

    print(f"Object validation smoke: {len(object_paths)} files")

    for object_path in object_paths:
        try:
            with object_path.open("r", encoding="utf-8") as file:
                raw_definition = json.load(file)
        except Exception as exc:
            total_errors += 1
            print(f"[ERROR] {object_path.name}: cannot read JSON: {exc}")
            continue

        object_id = object_path.stem
        raw_errors, raw_warnings = validate_object_definition(
            raw_definition,
            object_id=object_id,
        )
        for issue in raw_errors + raw_warnings:
            print(
                f"[{issue.severity.upper()}] "
                f"{object_path.name}: {issue.message}"
            )
        total_errors += len(raw_errors)
        total_warnings += len(raw_warnings)

        normalized_definition = normalize_object_definition(raw_definition, object_id)
        functional_type = normalized_definition.get("functional_type", "decorative")
        normalized_counts[functional_type] = normalized_counts.get(functional_type, 0) + 1

        errors, warnings = validate_object_definition(
            normalized_definition,
            object_id=object_id,
        )
        if errors or warnings:
            print(f"After normalization: {object_path.name}")
            total_errors += len(errors)
            total_warnings += len(warnings)

            for issue in errors + warnings:
                print(
                    f"[{issue.severity.upper()}] "
                    f"{object_path.name}: {issue.message}"
                )

    print("Functional type counts:")
    for functional_type in sorted(normalized_counts):
        print(f"  {functional_type}: {normalized_counts[functional_type]}")

    print(f"Result: {total_errors} errors, {total_warnings} warnings")
    return total_errors == 0


if __name__ == "__main__":
    raise SystemExit(0 if run_smoke() else 1)
