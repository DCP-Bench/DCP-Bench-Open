"""Check stored submissions with the shared evaluator and update their record.json."""
import argparse
import json
from pathlib import Path
from evaluation import evaluate
from evaluation.legacy import metrics, solver_id

ROOT = Path(__file__).resolve().parent


def verify_model(model_path):
    model_path = Path(model_path)
    framework = model_path.parent.parent.name
    problem = model_path.parent.parent.parent.name
    sidecar = model_path.parent / "record.json"
    try:
        existing = json.loads(sidecar.read_text(encoding="utf-8")) if sidecar.exists() else {}
    except ValueError:
        existing = {}
    result = evaluate(model_path, problem, solver_id(framework), legacy=True)
    return metrics(result, problem, solver_id(framework), existing)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem", default="abbots_puzzle")
    parser.add_argument("--model", type=Path)
    args = parser.parse_args()
    models = [args.model] if args.model else sorted((ROOT / "generated_models" / args.problem).glob("*/*/model.*"))
    models = [p for p in models if p.suffix in (".py", ".mzn")]
    if not models:
        print("No models found.")
        return 1
    failures = 0
    for model in models:
        record = verify_model(model)
        (model.parent / "record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        accepted = record["evaluation"]["accepted"]
        failures += not accepted
        print(f"{'PASS' if accepted else 'FAIL'} {model}: {record['evaluation']['reason']}")
    print(f"{len(models) - failures}/{len(models)} accepted")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
