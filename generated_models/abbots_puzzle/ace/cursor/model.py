import sys
import json
import os
import tempfile

# PyCSP3's import-time loader requires argv[0] to end with ".py";
# verify_models.py copies the script to a *.__hidden_py__ tempfile.
_argv = sys.argv
sys.argv = [""]
from pycsp3 import *
sys.argv = _argv

# Decision variables: number of men, women, and children
men = Var(range(0, 101))
women = Var(range(0, 101))
children = Var(range(0, 101))

satisfy(
    # 100 people in total
    men + women + children == 100,
    # 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
    6 * men + 4 * women + children == 200,
    # Five times as many women as men
    women == 5 * men,
)

with tempfile.TemporaryDirectory() as tmp:
    xml_path = os.path.join(tmp, "abbots")
    status = solve(verbose=-1, filename=xml_path)
if status is not SAT:
    raise SystemExit("No solution found.")

print(json.dumps({
    "men": int(value(men)),
    "women": int(value(women)),
    "children": int(value(children)),
}))
