"""Runner protocol for the swipl_clpfd integration. Runs inside the image only.

A submission is a Prolog program stating the model; SWI-Prolog's own search is
what solves it, so the solving side lives in `driver.pl` next to this file and
runs in a separate `swipl` process. This module owns the process: it starts the
driver, keeps it inside the execution budget, and turns what it printed into the
runner protocol, emitting exactly one status whatever the driver did.

Keeping the two apart is deliberate. The driver cannot outlive its budget or
print more solutions than were asked for, because this module, not the driver,
decides what reaches the evaluator.
"""
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish  # noqa: E402

INPUT = Path("/input")
DRIVER = "/opt/runner/driver.pl"
# The driver stops itself at the execution budget; this is the backstop for a
# process that ignored it, and stays inside the container's own wall clock.
GRACE_SECONDS = 4
STATUSES = ("complete", "limit", "timeout", "unsat", "error", "unsupported")


def driver_records(budget):
    """Run the driver and return the JSON records it printed, or a failure."""
    started = time.monotonic()
    try:
        finished = subprocess.run(
            ["swipl", "--stack-limit=1g", "--no-tty", "-g", "main", "-t", "halt(1)", DRIVER],
            capture_output=True, text=True, timeout=budget + GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        return None, ("timeout", "The driver outlived the execution budget")
    sys.stderr.write(finished.stderr)
    records = []
    for line in finished.stdout.splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except ValueError:
            return None, ("error", f"The driver printed a line that is not JSON: {line[:200]}")
    if not records:
        elapsed = time.monotonic() - started
        detail = f"swipl exited {finished.returncode} after {elapsed:.1f}s without a verdict"
        return None, ("error", f"{detail}: {finished.stderr[-2000:]}")
    return records, None


def relay(records, solution_limit):
    """Re-emit the driver's records, capped at the solutions that were asked for."""
    solutions = [record for record in records if record.get("type") == "solution"]
    statuses = [record for record in records if record.get("type") == "status"]
    if len(statuses) != 1 or statuses[-1] is not records[-1]:
        return finish("error", "The driver did not end with exactly one status record")
    status = statuses[0]
    if status.get("status") not in STATUSES:
        return finish("error", f"The driver reported an unknown status {status.get('status')!r}")
    for record in solutions[:solution_limit]:
        values = record.get("values")
        if not isinstance(values, dict) or not values:
            return finish("error", "The driver emitted a solution without declared outputs")
        emit({"type": "solution", "values": values})
    if len(solutions) > solution_limit:
        # The driver is not allowed to answer a question that was not asked;
        # report the excess rather than passing it on as if it were requested.
        return finish("error", f"The driver emitted {len(solutions)} solutions, "
                               f"more than the {solution_limit} requested")
    detail = status.get("detail") or ""
    extra = {"solve_seconds": status["solve_seconds"]} if "solve_seconds" in status else {}
    finish(status["status"], detail, **extra)


def main():
    try:
        request = json.loads((INPUT / "request.json").read_text())
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by swipl_clpfd")
        records, failure = driver_records(request["execution_timeout"])
        if failure is not None:
            return finish(*failure)
        relay(records, request["solution_limit"])
    except Exception as error:  # noqa: BLE001 - the runner always reports a status
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))


if __name__ == "__main__":
    main()
