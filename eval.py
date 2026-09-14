"""Legacy JSONL CLI; uses the container-based evaluation package."""
import json
from pathlib import Path
import tempfile
import click
from evaluation import evaluate
from evaluation.legacy import solver_id
from evaluation.results import strict_json


@click.command()
@click.option("--dataset_file", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--test_file", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--modelling_framework", required=True)
def main(dataset_file, test_file, modelling_framework):
    """Check embedded-example submissions, one solution each. Images must already exist."""
    dataset = {item["id"]: item for line in dataset_file.read_text(encoding="utf-8").splitlines()
               if line.strip() for item in [strict_json(line)]}
    results = []
    with tempfile.TemporaryDirectory(prefix="dcp_legacy_") as temp:
        for line in test_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            submission = strict_json(line)
            problem = submission["id"]
            gt = dataset.get(problem)
            if gt is None:
                results.append({"accepted": False, "reason": "reference_error", "problem_id": problem,
                                "detail": "Problem missing from supplied dataset"})
                continue
            extension = ".mzn" if solver_id(modelling_framework) == "minizinc_gecode" else ".py"
            model_path = Path(temp) / ("model" + extension)
            model_path.write_text(submission["model"], encoding="utf-8")
            source = "# Data\n" + gt.get("example_instance", "") + "\n# End of data\n" + gt["model"]
            results.append(evaluate(model_path, problem, solver_id(modelling_framework), legacy=True,
                                    reference_source=source, instances=[]))
    report = {"accepted": bool(results) and all(x["accepted"] for x in results), "results": results}
    Path("summary.txt").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    # The terminal gets the verdicts; summary.txt keeps the full record. A model
    # is rejected for a reason, so print the reason rather than a bare failure.
    width = max((len(x.get("problem_id", "")) for x in results), default=0)
    for item in results:
        detail = item.get("detail") or ""
        # "Legacy process exited 1" says nothing useful; the exception that
        # actually ended the run is the last line the model wrote to stderr.
        for instance in item.get("instances") or []:
            lines = [line for line in (instance.get("stderr") or "").splitlines() if line.strip()]
            if lines and item.get("reason") == "execution_error":
                detail = lines[-1].strip()
        click.echo(f"{'PASS' if item['accepted'] else 'FAIL'} {item.get('problem_id', ''):<{width}}  "
                   f"{item.get('reason', '')}{'  ' + detail if detail else ''}".rstrip())
    passed = sum(1 for x in results if x["accepted"])
    click.echo(f"\n{passed}/{len(results)} accepted. Full JSON in summary.txt.")
    if not report["accepted"]:
        raise click.exceptions.Exit(1)


if __name__ == "__main__":
    main()
