"""Runner protocol for the eclipse_clp integration. Runs inside the image only.

A submission is an ECLiPSe program stating the model; ECLiPSe's own search is what
solves it, so the solving side lives in `driver.ecl` next to this file and runs in
a separate `eclipse.exe` process. This module owns the process: it converts the
instance to an ECLiPSe term, starts the driver, keeps it inside the execution
budget, and turns what it wrote into the runner protocol, emitting exactly one
status whatever the driver did.

The driver writes its records to a file of its own rather than to standard output,
so a submission that prints cannot corrupt them; everything the process prints is
forwarded to stderr. The verdict is read from the driver's status record, never
from the exit code: ECLiPSe exits 0 after errors.

Keeping the two apart is deliberate. The driver cannot outlive its budget or
report more solutions than were asked for, because this module, not the driver,
decides what reaches the evaluator.
"""
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish  # noqa: E402

INPUT = Path("/input")
DRIVER = "/opt/runner/driver.ecl"
ECLIPSE = "/opt/eclipse/lib/x86_64_linux/eclipse.exe"
REQUEST = Path("/tmp/dcp_request.ecl")
PROTOCOL = Path("/tmp/dcp_protocol.jsonl")
MESSAGES = Path("/tmp/dcp_messages.txt")
STDOUT = Path("/tmp/dcp_stdout.txt")
# The driver stops itself at the execution budget; this is the backstop for a
# process that ignored it (a long propagation in the solver does not see the
# alarm until it returns), and stays inside the container's own wall clock.
GRACE_SECONDS = 4
STATUSES = ("complete", "limit", "timeout", "unsat", "error", "unsupported")


def quoted(text, quote):
    """ECLiPSe quoted text: backslash escapes for the quote, backslash and controls."""
    pieces = [quote]
    for char in text:
        if char in (quote, "\\"):
            pieces.append("\\" + char)
        elif char == "\n":
            pieces.append("\\n")
        elif char == "\t":
            pieces.append("\\t")
        elif ord(char) < 32 or ord(char) == 127:
            pieces.append("\\%03o\\" % ord(char))
        else:
            pieces.append(char)
    pieces.append(quote)
    return "".join(pieces)


def term(value):
    """The ECLiPSe term for a JSON value.

    Integers (bignums too) and floats are numbers, true/false/null the atoms of
    those names, strings ECLiPSe strings, arrays lists, and objects lists of
    Key-Value pairs with atom keys. Pairs are written as -(Key, Value) so no
    operator declaration is needed to read them.
    """
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"Non-finite number in the instance: {value}")
        text = repr(value)
        if "e" in text:
            mantissa, exponent = text.split("e")
            if "." not in mantissa:
                mantissa += ".0"
            text = f"{mantissa}e{int(exponent)}"
        return text
    if isinstance(value, str):
        return quoted(value, '"')
    if isinstance(value, list):
        return "[" + ", ".join(term(item) for item in value) + "]"
    if isinstance(value, dict):
        return "[" + ", ".join(f"-({quoted(key, chr(39))}, {term(item)})"
                               for key, item in value.items()) + "]"
    raise ValueError(f"Cannot convert {type(value).__name__} to an ECLiPSe term")


def read_text(path, limit=2000):
    try:
        return path.read_text(errors="replace")[-limit:]
    except OSError:
        return ""


def driver_records(request, started):
    """Run the driver and return the JSON records it wrote, or a failure."""
    budget = request["execution_timeout"]
    for path in (PROTOCOL, MESSAGES, STDOUT):
        path.unlink(missing_ok=True)
    left = budget - (time.monotonic() - started)
    REQUEST.write_text(f"request({term(request['instance'])}, {int(request['solution_limit'])}, "
                       f"{max(left, 0.001)!r}).\n", encoding="utf-8")
    environment = dict(os.environ, ECLIPSEDIR="/opt/eclipse",
                       LD_LIBRARY_PATH="/opt/eclipse/lib/x86_64_linux")
    with STDOUT.open("w") as printed:
        driver = subprocess.Popen([ECLIPSE, "-f", DRIVER, "-e", "dcp_main"],
                                  stdin=subprocess.DEVNULL, stdout=printed, stderr=printed,
                                  env=environment)
        killed = False
        try:
            driver.wait(timeout=max(left, 0) + GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            killed = True
            driver.kill()
            driver.wait()
    # What the process printed and the messages ECLiPSe wrote are logs.
    sys.stderr.write(read_text(STDOUT, 1_000_000))
    sys.stderr.write(read_text(MESSAGES, 1_000_000))
    lines = read_text(PROTOCOL, 100_000_000).splitlines()
    records = []
    for line in lines:
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except ValueError:
            # A partial last line is what a killed driver leaves behind.
            if not killed:
                return None, ("error", f"The driver wrote a line that is not JSON: {line[:200]}")
    if killed and not any(record.get("type") == "status" for record in records):
        return None, ("timeout", "The driver outlived the execution budget")
    if not records:
        detail = f"eclipse.exe exited {driver.returncode} without a verdict"
        return None, ("error", f"{detail}: {read_text(MESSAGES) or read_text(STDOUT)}")
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
    if len(solutions) > solution_limit:
        # The driver is not allowed to answer a question that was not asked;
        # report the excess rather than passing it on as if it were requested.
        return finish("error", f"The driver emitted {len(solutions)} solutions, "
                               f"more than the {solution_limit} requested")
    for record in solutions:
        values = record.get("values")
        if not isinstance(values, dict) or not values:
            return finish("error", "The driver emitted a solution without declared outputs")
        emit({"type": "solution", "values": values})
    detail = status.get("detail") or ""
    extra = {"solve_seconds": status["solve_seconds"]} if "solve_seconds" in status else {}
    finish(status["status"], detail, **extra)


def main():
    started = time.monotonic()
    try:
        request = json.loads((INPUT / "request.json").read_text())
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by eclipse_clp")
        records, failure = driver_records(request, started)
        if failure is not None:
            return finish(*failure)
        relay(records, request["solution_limit"])
    except Exception as error:  # noqa: BLE001 - the runner always reports a status
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))


if __name__ == "__main__":
    main()
