"""Read a JSON instance, write an Essence' parameter file, run Savile Row, print the result.

Usage: python3 solve.py [data.json]   (default: data.json next to this script)
Only the Python standard library is used (json, subprocess, tempfile).
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def matrix(value):
    """An Essence' matrix literal for a (nested) list of ints or bools."""
    if isinstance(value, list):
        return "[" + ", ".join(matrix(item) for item in value) + "]"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(int(value))


def param_file(data):
    """Only the keys the model uses; every size comes from the data; the ragged list is padded."""
    wishes = data["wishes"]
    width = max(len(row) for row in wishes)
    lettings = {
        "n_people": len(wishes),
        "n_slots": len(data["capacity"]),
        "max_wishes": width,
        "capacity": data["capacity"],
        "wishes": [row + [0] * (width - len(row)) for row in wishes],
        "wishes_len": [len(row) for row in wishes],
    }
    return "language ESSENCE' 1.0\n" + "".join(f"letting {k} = {matrix(v)}\n" for k, v in lettings.items())


def parse(text):
    """`letting NAME be VALUE` lines of one solution -> dict (ints, bools, nested lists)."""
    values = {}
    for name, value in re.findall(r"letting (\w+) be (.*?)\n(?=letting|\n|-|$)", text, re.S):
        value = re.sub(r";\s*int\([^)]*\)", "", value)          # drop index-domain annotations
        value = value.replace("true", "1").replace("false", "0")
        values[name] = json.loads(value)
    return values


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "data.json"
    data = json.loads(path.read_text())
    with tempfile.TemporaryDirectory() as work:      # Savile Row and Minion write files next to the param file
        param = Path(work) / "data.param"
        param.write_text(param_file(data))
        run = subprocess.run(["savilerow", str(HERE / "assign.eprime"), str(param), "-run-solver",
                              "-solutions-to-stdout"], cwd=work, capture_output=True, text=True)
        info = (Path(work) / "data.param.info").read_text() if (Path(work) / "data.param.info").exists() else ""
    if run.returncode != 0:
        sys.exit("Savile Row failed:\n" + run.stdout + run.stderr)
    if "SolverSatisfiable:0" in info:
        print("no assignment exists")
        return
    if "SolverTimeOut:0" not in info:
        print("warning: search stopped early; the result is not proven optimal")
    solution = parse(run.stdout.split("----------")[0])
    print(f"first wishes granted: {solution['first_wishes']}")
    for person, slot in enumerate(solution["slot"], start=1):
        print(f"person {person} -> slot {slot}")


if __name__ == "__main__":
    main()
