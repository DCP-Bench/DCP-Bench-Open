"""Readiness checks for the pumpkin_rust integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver pumpkin_rust` runs this and keeps
its output as the readiness evidence.

A submission is one Rust file defining `build`, spliced into a binary that the
image compiles against a prebuilt driver library, so this integration also has
to prove that a submission which does not compile is reported as
`compilation_error` rather than as some downstream failure. Every check below
pays a real `rustc` invocation.

Three checks deserve a word on what they actually assert. `malformed_output`
uses a submission that writes junk on stdout: the driver owns that stream for
the JSONL protocol, so anything a model prints there corrupts it, and the
evaluator has to reject the run rather than parse around it. `timeout_cleanup`
uses an unsatisfiable pigeonhole rather than a sleep, so it also exercises the
path where Pumpkin itself is still searching when the budget runs out.
`native_api` guards the mistake this integration was rebuilt to fix: the handle
a submission is given is `pumpkin_solver::Solver` itself, and constraints are
posted through Pumpkin's own constructors rather than a wrapper of ours.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "pumpkin_rust"

# A tiny trusted reference, kept here so this script does not depend on the
# test suite. n=2 gives x+y==2 exactly three solutions.
REFERENCE = '''
# Data
n = 2
optimize = False
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y >= n if optimize else x + y == n)
if optimize:
    model.minimize(x + y)
model.solve()
solution = {"x": int(x.value()), "y": y.value()}
print(json.dumps(solution))
'''
OPTIMIZING = REFERENCE.replace("optimize = False", "optimize = True")
MAXIMIZING = OPTIMIZING.replace("model.minimize", "model.maximize")

HEAD = "fn build(inst: &Instance, solver: &mut Solver) -> Model {\n"
TAIL = "}\n"
DECLARE = ("    let n = inst.int(\"n\");\n"
           "    let x = solver.new_bounded_integer(0, n);\n"
           "    let y = solver.new_bounded_integer(0, n);\n")
EXPORT = ("    let mut m = Model::new();\n"
          "    m.put(\"x\", x);\n"
          "    m.put(\"y\", y);\n")
POST = ("    let tag = solver.new_constraint_tag();\n"
        "    solver.add_constraint(pumpkin_solver::{}).post();\n")

GOOD = (HEAD + DECLARE
        + POST.format("equals(vec![x.scaled(1), y.scaled(1)], n, tag)")
        + EXPORT + "    m\n" + TAIL)
# `n` is a maximum here, so the objective has room to move in both directions.
# A lower bound is written as an upper bound on the negated terms, which is what
# Pumpkin offers: there is no `greater_than_or_equals`.
OPTIMAL = (HEAD + DECLARE
           + POST.format("less_than_or_equals(vec![x.scaled(-1), y.scaled(-1)], -n, tag)")
           + "    let total = solver.new_bounded_integer(0, 2 * n);\n"
           + POST.format("equals(vec![x.scaled(1), y.scaled(1), total.scaled(-1)], 0, tag)")
           + EXPORT + "    m.DIRECTION(total);\n    m\n" + TAIL)
# Compiles and solves, then corrupts the protocol stream the driver owns.
MALFORMED = (HEAD + DECLARE
             + POST.format("equals(vec![x.scaled(1), y.scaled(1)], n, tag)")
             + "    println!(\"this is not a protocol record\");\n"
             + EXPORT + "    m\n" + TAIL)
UNSATISFIABLE = (HEAD + DECLARE
                 + POST.format("equals(vec![x.scaled(1)], 0, tag)")
                 + POST.format("equals(vec![x.scaled(1)], 1, tag)")
                 + EXPORT + "    m\n" + TAIL)
# 40 pigeons into 39 holes: satisfiable-looking, genuinely unsatisfiable, and
# slow enough that a two-second budget expires inside Pumpkin's search.
SLOW = (HEAD + DECLARE
        + POST.format("equals(vec![x.scaled(1), y.scaled(1)], n, tag)")
        + "    let birds: Vec<Var> = (0..40)\n"
        + "        .map(|_| solver.new_bounded_integer(0, 38))\n"
        + "        .collect();\n"
        + POST.format("all_different(birds, tag)")
        + EXPORT + "    m\n" + TAIL)
UNCOMPILABLE = "this is not Rust\n"
# Pumpkin's AffineView::scaled multiplies the existing scale without rechecking
# it, so `v.scaled(0)` builds a zero-scaled view that later divides by zero
# inside a propagator. Instance data carrying a zero weight is ordinary, so a
# model has to drop those terms itself, and a term list emptied that way still
# has to post a valid constraint. That is what the modelling skill tells models
# to do, and this is what keeps the advice honest.
ZERO_COEFFICIENTS = (
    HEAD + DECLARE
    + "    let padding = solver.new_bounded_integer(0, 5);\n"
    + "    let weights = [1, 1, 0];\n"
    + "    let vars = [x, y, padding];\n"
    + "    let kept: Vec<Term> = weights.iter().zip(vars)\n"
    + "        .filter(|(&w, _)| w != 0)\n"
    + "        .map(|(&w, v)| v.scaled(w))\n"
    + "        .collect();\n"
    + POST.format("equals(kept, n, tag)")
    + "    // Every weight zero: the sum is the constant zero, and the\n"
    + "    // constraint is posted over that rather than over an empty list.\n"
    + "    let all_zero = [0, 0, 0];\n"
    + "    let spare: Vec<Var> = (0..3)\n"
    + "        .map(|_| solver.new_bounded_integer(0, 4))\n"
    + "        .collect();\n"
    + "    let survivors: Vec<Term> = all_zero.iter().zip(&spare)\n"
    + "        .filter(|(&w, _)| w != 0)\n"
    + "        .map(|(&w, &v)| v.scaled(w))\n"
    + "        .collect();\n"
    + "    let zero = solver.new_bounded_integer(0, 0);\n"
    + "    let terms = if survivors.is_empty() { vec![zero.scaled(1)] } else { survivors };\n"
    + POST.format("less_than_or_equals(terms, 0, tag)")
    + EXPORT + "    m\n" + TAIL)

# Rust can inspect its own container, so this check runs through the real
# submission path. A failed probe panics, which the driver reports as an
# execution error, so the check only passes when every probe held.
ISOLATED = '''fn build(inst: &Instance, solver: &mut Solver) -> Model {
    use std::collections::BTreeSet;
    use std::net::TcpStream;
    use std::time::Duration;

    // Effective uid: /proc/self/status reports it without an extra crate.
    let status = std::fs::read_to_string("/proc/self/status").expect("cannot read /proc/self/status");
    let uid_line = status
        .lines()
        .find(|line| line.starts_with("Uid:"))
        .expect("no Uid line in /proc/self/status");
    let uid: u32 = uid_line.split_whitespace().nth(1).unwrap().parse().unwrap();
    assert_ne!(uid, 0, "container runs as root");

    assert!(!std::path::Path::new("/dataset").exists(), "dataset is visible to the candidate");

    let entries: BTreeSet<String> = std::fs::read_dir("/input")
        .expect("cannot list /input")
        .map(|entry| entry.unwrap().file_name().to_string_lossy().into_owned())
        .collect();
    let expected: BTreeSet<String> =
        ["model.rs".to_string(), "request.json".to_string()].into_iter().collect();
    assert_eq!(entries, expected, "unexpected /input");

    assert!(std::fs::write("/input/written", b"x").is_err(), "input is writable");

    let address: std::net::SocketAddr = "1.1.1.1:443".parse().expect("address");
    let reachable = TcpStream::connect_timeout(&address, Duration::from_millis(500)).is_ok();
    assert!(!reachable, "network reachable");

    let n = inst.int("n");
    let x = solver.new_bounded_integer(0, n);
    let y = solver.new_bounded_integer(0, n);
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![x.scaled(1), y.scaled(1)], n, tag)).post();
    let mut m = Model::new();
    m.put("x", x);
    m.put("y", y);
    m
}
'''

# The driver must hand over Pumpkin itself and wrap none of its modelling API.
NATIVE = '''fn build(inst: &Instance, solver: &mut Solver) -> Model {
    // The handle a submission is given is Pumpkin's own Solver. This binding
    // would not typecheck against a wrapper.
    let checked: &mut pumpkin_solver::Solver = solver;

    let n = inst.int("n");
    let x = checked.new_bounded_integer(0, n);
    let y = checked.new_bounded_integer(0, n);
    // Posted through Pumpkin's own constraint constructors and its own tag.
    let tag = checked.new_constraint_tag();
    checked
        .add_constraint(pumpkin_solver::equals(vec![x.scaled(1), y.scaled(1)], n, tag))
        .post();
    let spare: Vec<Var> = (0..3).map(|_| checked.new_bounded_integer(1, 3)).collect();
    let tag = checked.new_constraint_tag();
    checked
        .add_constraint(pumpkin_solver::all_different(spare, tag))
        .post();

    let mut m = Model::new();
    m.put("x", x);
    m.put("y", y);
    m
}
'''


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / f"{name}.rs"
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, **kwargs):
            result = evaluate(candidate(name, source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            return result

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL.replace("DIRECTION", "minimise"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximise"), reference=MAXIMIZING)
        check("native_api", NATIVE)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)
        check("compilation_error", UNCOMPILABLE, expected={"compilation_error"})
        check("zero_coefficients", ZERO_COEFFICIENTS)

    try:
        image_identity({"id": SOLVER, "image": "dcp-eval/definitely-absent:readiness"})
        results["missing_image"] = False
    except EvaluationError as error:
        results["missing_image"] = error.reason == "infrastructure_error"

    print(json.dumps(results, sort_keys=True))
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
