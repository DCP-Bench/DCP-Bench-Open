"""Runner protocol for the picat integration. Runs inside the image only.

A submission is a Picat program stating the model; Picat's own solvers are what
solve it, so the solving side lives in `driver.pi` next to this file and runs in
a separate `picat` process. This module owns that process: it turns the JSON
instance into a Picat term, starts the driver, keeps it inside the execution
budget, and turns what the driver recorded into the runner protocol, emitting
exactly one status whatever the driver did.

The driver writes its records to a file rather than to standard output, so that
anything the submission or Picat prints is relayed to stderr as a log and never
mistaken for a solution.
"""
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish, strict_loads  # noqa: E402

INPUT = Path("/input")
PICAT = "/opt/picat/picat"
DRIVER = "/opt/runner/driver.pi"
# Time kept back from the execution budget for this module to report after it
# stops the driver; the evaluator's own clock allows ten seconds beyond it.
MARGIN_SECONDS = 1.0
STATUSES = ("complete", "limit", "timeout", "unsat", "error", "unsupported")
# Picat colours its syntax-error marker; the escape codes are dropped from details.
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def atom(text):
    """A quoted Picat atom, which is what every instance key becomes."""
    return "'" + text.replace("\\", "\\\\").replace("'", "\\'") + "'"


def string(text):
    escaped = []
    for char in text:
        if char in "\\\"":
            escaped.append("\\" + char)
        elif char == "\n":
            escaped.append("\\n")
        elif char == "\t":
            escaped.append("\\t")
        elif ord(char) < 32:
            raise ValueError(f"Instance string holds control character {ord(char)}, which has no Picat escape here")
        else:
            escaped.append(char)
    return '"' + "".join(escaped) + '"'


def term(value):
    """The instance value as Picat term text for read_term/1.

    Arrays become lists and objects json_object(Keys, Values), which the driver
    turns into maps. Picat has no Boolean type, and its constraints read 1 as
    true, so JSON true and false become 1 and 0.
    """
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Instance holds a non-finite number")
        return repr(value)
    if isinstance(value, str):
        return string(value)
    if value is None:
        return "null"
    if isinstance(value, list):
        return "[" + ", ".join(term(item) for item in value) + "]"
    if isinstance(value, dict):
        keys = ", ".join(atom(key) for key in value)
        values = ", ".join(term(item) for item in value.values())
        return f"json_object([{keys}], [{values}])"
    raise ValueError(f"Instance value of type {type(value).__name__} is not JSON")


def run_driver(request, workdir):
    """Run the driver and return (records, killed, stderr text)."""
    request_file = workdir / "request.txt"
    record_file = workdir / "records.jsonl"
    request_file.write_text(
        f"dcp_request({term(request['instance'])}, {int(request['solution_limit'])}, "
        f"{string(str(INPUT / 'model.pi'))}).\n", encoding="utf-8")
    record_file.write_text("", encoding="utf-8")
    budget = max(0.5, request["execution_timeout"] - MARGIN_SECONDS)
    killed = False
    with tempfile.TemporaryFile("w+") as log:
        driver = subprocess.Popen([PICAT, DRIVER, str(request_file), str(record_file)],
                                  stdin=subprocess.DEVNULL, stdout=log, stderr=log, cwd=workdir)
        try:
            driver.wait(timeout=budget)
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
        return finish("error", f"picat exited {returncode} without a verdict: {output[-2000:]}")
    status = statuses[0]
    if status.get("status") not in STATUSES:
        return finish("error", f"The driver reported an unknown status {status.get('status')!r}")
    detail = status.get("detail") or ""
    printed = ANSI.sub("", output).strip()
    if status["status"] == "error" and printed:
        # A syntax error is reported by Picat's compiler on its own output, and
        # the thrown term alone does not say where it is.
        detail = f"{detail}; picat printed: {printed[-1500:]}"
    finish(status["status"], detail)


def main():
    try:
        started = time.monotonic()
        request = strict_loads((INPUT / "request.json").read_text(encoding="utf-8"))
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by picat")
        with tempfile.TemporaryDirectory(prefix="picat_") as directory:
            request = dict(request, execution_timeout=request["execution_timeout"] - (time.monotonic() - started))
            records, killed, output, returncode = run_driver(request, Path(directory))
        sys.stderr.write(output)
        relay(records, killed, request["solution_limit"], output, returncode)
    except Exception as error:  # noqa: BLE001 - the runner always reports a status
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))


if __name__ == "__main__":
    main()
