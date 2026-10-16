"""Runs every case folder under probes/cases through the maxicp_java image and prints the status lines (probe scaffolding)."""
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
selected = sys.argv[1:]
for case in sorted((HERE / "cases").iterdir()):
    if selected and case.name not in selected:
        continue
    start = time.monotonic()
    try:
        done = subprocess.run(["sh", str(HERE / "runcase.sh"), str(case)], capture_output=True, text=True, timeout=150)
        out, err = done.stdout, done.stderr
    except subprocess.TimeoutExpired as error:
        out, err = (error.stdout or b"").decode(errors="replace"), "TIMEOUT"
    lines = [line[:220] for line in out.splitlines() if line.strip()]
    print(f"== {case.name} ({time.monotonic() - start:.1f}s)")
    for line in lines[:12]:
        print("   ", line)
    if len(lines) > 12:
        print("    ... %d more lines" % (len(lines) - 12))
    tail = [line for line in err.splitlines() if line.strip()][-3:]
    if tail:
        print("    stderr tail:", " | ".join(t[:160] for t in tail))
