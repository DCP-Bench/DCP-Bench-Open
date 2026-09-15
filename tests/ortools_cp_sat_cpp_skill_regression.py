"""Regression for the ortools-cp-sat-cpp skill's AddElement guidance.

Takes a skill bundle path and checks two things about one trap:

1. that the trap is real, by running the broken and the repaired model through
   the container evaluator and requiring the reported outcomes to differ in the
   documented way, and
2. that the bundle warns about it.

The trap: `CpModelBuilder::AddElement` in OR-Tools 9.15 takes its array as
`absl::Span<const LinearExpr>` (or a span of `int64_t` constants). A
`std::vector<IntVar>`, which is what a model naturally has on hand, does not
convert to either, so the submission fails to compile — and a compile failure
costs a whole model attempt, since the evaluator never gets as far as search.
The repair is one line: build a `std::vector<LinearExpr>` from the variables
and pass that.

A bundle that does not carry the guidance fails, which is what makes this a
check of the instructions rather than of the integration alone. The trap cost
the first model attempt of the run that produced this script:
`generation/runs/20260915T153604-c7f2/attempts/bales_of_hay/ortools_cp_sat_cpp/attempt-001`
was rejected as `compilation_error` and attempt-002 was accepted.
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation import evaluate  # noqa: E402

REFERENCE = '''
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y == n)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''

HEADER = '''#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  IntVar x = model.NewIntVar(Domain(0, n));
  IntVar y = model.NewIntVar(Domain(0, n));
  model.AddEquality(x + y, n);

  // Read y back out of a one-entry table at a variable position, which is the
  // shape every element constraint in this corpus takes.
  std::vector<IntVar> table = {y};
  IntVar position = model.NewIntVar(Domain(0, 0));
  IntVar picked = model.NewIntVar(Domain(0, n));
'''

FOOTER = '''  model.AddEquality(picked, y);
  outputs = {{"x", x.index()}, {"y", y.index()}};
}
'''

# Broken: a vector<IntVar> matches no AddElement overload.
RAW_VECTOR = HEADER + "  model.AddElement(position, table, picked);\n" + FOOTER

# Repaired: convert to the span of LinearExpr the overload actually takes.
CONVERTED = (HEADER
             + "  const std::vector<LinearExpr> exprs(table.begin(), table.end());\n"
               "  model.AddElement(position, exprs, picked);\n"
             + FOOTER)

GUIDANCE = ("addelement", "linearexpr")


def outcome(directory, name, source):
    path = Path(directory) / f"{name}.cpp"
    path.write_text(source, encoding="utf-8")
    result = evaluate(path, "addelement_regression", "ortools_cp_sat_cpp",
                      reference_source=REFERENCE, execution_timeout=30)
    return result["accepted"], result["reason"]


def documented(text, words):
    return any(all(word in line.lower() for word in words) for line in text.splitlines())


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: ortools_cp_sat_cpp_skill_regression.py SKILL_BUNDLE")
    bundle = Path(sys.argv[1])
    skill = (bundle / "SKILL.md").read_text(encoding="utf-8")

    failures = []
    with tempfile.TemporaryDirectory(prefix="dcp_cpp_regression_") as directory:
        accepted, reason = outcome(directory, "raw_vector", RAW_VECTOR)
        if accepted or reason != "compilation_error":
            failures.append("the AddElement trap did not reproduce: "
                            f"accepted={accepted} reason={reason}")
        accepted, reason = outcome(directory, "converted", CONVERTED)
        if not accepted:
            failures.append(f"the repair was rejected: {reason}")

    if not documented(skill, GUIDANCE):
        failures.append(f"{bundle} has no line mentioning {' and '.join(GUIDANCE)}")

    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        raise SystemExit(1)
    print(f"ok {bundle}: the trap reproduces through the evaluator and is documented")


if __name__ == "__main__":
    main()
