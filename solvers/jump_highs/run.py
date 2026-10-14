"""Runner protocol for the jump_highs integration. Runs inside the image only.

A submission is a Julia file defining `build(instance)` that returns a JuMP model
and its declared outputs. The solving side lives in `driver.jl` next to this
file and runs in a separate `julia` process; this module owns that process. It
starts the driver with a deadline, stops it if it outlives the execution budget,
and turns what the driver recorded into the runner protocol, emitting exactly
one status whatever the driver did.

The driver writes its records to a file rather than to standard output, so that
anything the submission or HiGHS prints is relayed to stderr as a log and never
mistaken for a solution.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish, strict_loads  # noqa: E402

INPUT = Path("/input")
DRIVER = "/opt/runner/driver.jl"
# The driver gets the budget less this, to report a timeout itself; the process
# is stopped this much after the budget if it has not. The evaluator's own clock
# allows ten seconds beyond the budget.
DRIVER_MARGIN = 2.0
KILL_MARGIN = 1.0
STATUSES = ("complete", "limit", "timeout", "unsat", "error", "unsupported")


def run_driver(budget, workdir):
    """Run the driver and return (records, killed, printed output, exit code)."""
    record_file = workdir / "records.jsonl"
    record_file.write_text("", encoding="utf-8")
    deadline = time.time() + max(0.5, budget - DRIVER_MARGIN)
    killed = False
    with tempfile.TemporaryFile("w+") as log:
        driver = subprocess.Popen(
            ["julia", "--startup-file=no", "--history-file=no", DRIVER, str(record_file), repr(deadline)],
            stdin=subprocess.DEVNULL, stdout=log, stderr=log, cwd=workdir)
        try:
            driver.wait(timeout=max(0.5, budget - KILL_MARGIN))
        except subprocess.TimeoutExpired:
            driver.kill()
            driver.wait()
            killed = True
        log.seek(0)
        output = log.read()
    lines = [line for line in record_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    records = []
    for line in lines:
        try:
            records.append(strict_loads(line))
        except ValueError:
            # A record cut off by the kill is the only line that may be partial.
            if killed and line is lines[-1]:
                break
            raise ValueError(f"The driver wrote a record that is not JSON: {line[:200]}")
    return records, killed, output, driver.returncode


def relay(records, killed, solution_limit, output, returncode):
    """Re-emit the driver's records, capped at the solutions that were asked for."""
    solutions = [record for record in records if record.get("type") == "solution"]
    statuses = [record for record in records if record.get("type") == "status"]
    if len(solutions) > solution_limit:
        # The driver is not allowed to answer a question that was not asked.
        return finish("error", f"The driver emitted {len(solutions)} solutions, "
                               f"more than the {solution_limit} requested")
    for record in solutions:
        values = record.get("values")
        if not isinstance(values, dict) or not values:
            return finish("error", "The driver emitted a solution without declared outputs")
    if statuses and (len(statuses) != 1 or statuses[0] is not records[-1]):
        return finish("error", "The driver did not end with exactly one status record")
    for record in solutions:
        emit({"type": "solution", "values": record["values"]})
    if killed:
        return finish("timeout", "The execution budget ran out")
    if not statuses:
        return finish("error", f"julia exited {returncode} without a verdict: {output[-2000:]}")
    status = statuses[0]
    if status.get("status") not in STATUSES:
        return finish("error", f"The driver reported an unknown status {status.get('status')!r}")
    detail = status.get("detail") or ""
    if status["status"] == "error" and output.strip():
        # A syntax error's location is in Julia's own message, not only in the
        # exception the driver caught.
        detail = f"{detail}; julia printed: {output.strip()[-1500:]}"
    finish(status["status"], detail)


def main():
    try:
        started = time.monotonic()
        request = strict_loads((INPUT / "request.json").read_text(encoding="utf-8"))
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by jump_highs")
        budget = request["execution_timeout"] - (time.monotonic() - started)
        with tempfile.TemporaryDirectory(prefix="jump_") as directory:
            records, killed, output, returncode = run_driver(budget, Path(directory))
        sys.stderr.write(output)
        relay(records, killed, request["solution_limit"], output, returncode)
    except Exception as error:  # noqa: BLE001 - the runner always reports a status
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))


if __name__ == "__main__":
    main()
