"""Regression for the picat skill's warning about all_different/1 under sat.

Takes a skill bundle path and checks two things:

1. that the defect is real, by running the same small model through the
   container evaluator twice under `import sat.`: with `all_different/1` it is
   rejected as `invalid_solution`, and with pairwise `#!=` it is accepted, and
2. that the bundle warns about it.

A bundle that does not carry the warning fails, which is what makes this a check
of the instructions rather than of the integration alone. The defect cost a
model attempt in the run that produced this script:
`generation/runs/20260929T2116Z-picat-0895/attempts/de_bruijn_sequence/picat/attempt-001`.
"""
import sys
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation import evaluate  # noqa: E402

# Two numbers 0..3, all different, each written in binary by two 0/1 digits.
REFERENCE = '''
# Data
n = 2
# End of data
import cpmpy as cp
import json
z = cp.intvar(0, 3, shape=n, name="z")
bits = cp.boolvar(shape=(n, 2), name="bits")
model = cp.Model(cp.AllDifferent(z), [z[i] == 2 * bits[i, 0] + bits[i, 1] for i in range(n)])
model.solve()
solution = {"z": z.value().tolist(), "bits": bits.value().astype(int).tolist()}
print(json.dumps(solution))
'''

MODEL = """import sat.

model(Data, Vars, Outputs, Options) =>
    N = Data.get(n),
    Z = new_list(N),
    Z :: 0..3,
    DIFFERENT
    Bits = new_array(N, 2),
    Bits :: 0..1,
    foreach (I in 1..N)
        Z[I] #= 2 * Bits[I, 1] + Bits[I, 2]
    end,
    Vars = Z ++ vars(Bits),
    Outputs = [z = Z, bits = Bits],
    Options = [].
"""
GLOBAL = MODEL.replace("DIFFERENT", "all_different(Z),")
PAIRWISE = MODEL.replace("DIFFERENT", "foreach (I in 1..N-1, J in I+1..N) Z[I] #!= Z[J] end,")

WARNING = ("all_different", "pairwise", "sat")


def outcome(directory, name, source):
    path = Path(directory) / f"{name}.pi"
    path.write_text(source, encoding="utf-8")
    result = evaluate(path, "skill_regression", "picat", reference_source=REFERENCE,
                      solution_limit=2, execution_timeout=20)
    return result["accepted"], result["reason"]


def main():
    bundle = Path(sys.argv[1])
    text = (bundle / "SKILL.md").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as directory:
        broken = outcome(directory, "global", GLOBAL)
        repaired = outcome(directory, "pairwise", PAIRWISE)
    real = broken == (False, "invalid_solution") and repaired[0] is True
    warned = all(word in text for word in WARNING) and "invalid_solution" in text
    print(f"defect reproduced: {real} (all_different {broken}, pairwise {repaired}); "
          f"skill warns: {warned}")
    if not (real and warned):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
