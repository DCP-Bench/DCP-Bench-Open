import json
import re
import shutil
import subprocess

smt = """
(set-logic QF_LIA)
(declare-const men Int)
(declare-const women Int)
(declare-const children Int)
(assert (and (>= men 0) (<= men 100)))
(assert (and (>= women 0) (<= women 100)))
(assert (and (>= children 0) (<= children 100)))
; 100 people in total
(assert (= (+ men women children) 100))
; 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
(assert (= (+ (* 6 men) (* 4 women) children) 200))
; Five times as many women as men
(assert (= women (* 5 men)))
(check-sat)
(get-value (men women children))
"""

exe = shutil.which("yices-smt2")
if exe is None:
    raise SystemExit("yices-smt2 not found on PATH.")
result = subprocess.run(
    [exe, "--incremental"],
    input=smt,
    capture_output=True,
    text=True,
    check=False,
)
if result.returncode != 0 or "sat" not in result.stdout.splitlines()[:1] and "sat" not in result.stdout:
    raise SystemExit(result.stderr or result.stdout or "No solution found.")
if "unsat" in result.stdout.split():
    raise SystemExit("No solution found.")

found = {name: int(val) for name, val in re.findall(r"\((\w+)\s+(-?\d+)\)", result.stdout)}
if set(found) != {"men", "women", "children"}:
    raise SystemExit(f"Could not parse yices-smt2 output: {result.stdout}")
print(json.dumps(found))
