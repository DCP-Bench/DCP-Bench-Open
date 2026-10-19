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


# ---------------------------------------------------------------------------
# Bug-class checks (readiness level 2). The trusted references below are the
# cpmpy_python ones, copied verbatim; each submission is this integration's own
# Rust form of the same model.

EASY_MIN = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 10, name="x")
model = cp.Model(x >= n)
model.minimize(x)
model.solve()
solution = {"x": int(x.value())}
print(json.dumps(solution))
"""

STEP_REF = EASY_MIN.replace("x >= n", "x >= n - 1")

SUM_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 2, shape=4, name="x")
model = cp.Model(cp.sum(x) >= n)
model.minimize(cp.sum(x))
model.solve()
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
"""

SHAPES_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
cube = cp.intvar(0, 10, shape=(2, 2, 2), name="cube")
grid = cp.boolvar(shape=(2, 2), name="grid")
big = cp.intvar(0, 40000000000, name="big")
model = cp.Model([cube[i, j, k] == i + j + k + n for i in range(2) for j in range(2) for k in range(2)],
                 [grid[i, j] == (i == j) for i in range(2) for j in range(2)],
                 big == 30000000000 + n)
model.solve()
solution = {"cube": cube.value().tolist(), "grid": grid.value().tolist(), "big": int(big.value())}
print(json.dumps(solution))
"""

SHAPED_REF = """
# Data
n = 2
rows = [[1], [2, 3]]
mixed = [[1, "a"], [2, "b"]]
label = "first"
# End of data
import cpmpy as cp
import json
total = cp.intvar(0, 1000, name="total")
key = cp.intvar(0, 1000, name="key")
model = cp.Model(total == n + sum(sum(row) for row in rows), key == sum(row[0] for row in mixed))
model.solve()
solution = {"total": int(total.value()), "key": int(key.value())}
print(json.dumps(solution))
"""

SHAPED_INSTANCE = {"n": 3, "rows": [[4, 5, 6], [], [1]], "mixed": [[3, "c"]], "label": "second",
                   "name": "readiness", "note": "ragged rows, mixed rows, an unused string"}

LARGE_REF = """
# Data
n = 1500
# End of data
import cpmpy as cp
import json
b = cp.boolvar(shape=3000, name="b")
count = cp.intvar(0, 3000, name="count")
model = cp.Model(count == cp.sum(b), count == n)
model.solve()
solution = {"b": b.value().tolist(), "count": int(count.value())}
print(json.dumps(solution))
"""

# optimization_timeout: the submission adds an unrelated Golomb ruler (11 marks) to its
# objective, so Pumpkin finds a solution at once but cannot prove the optimum in 3 s.
UNPROVABLE = """fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.int("n");
    let x = solver.new_bounded_integer(0, 10);
    let marks: Vec<Var> = (0..11).map(|_| solver.new_bounded_integer(0, 200)).collect();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::less_than_or_equals(vec![x.scaled(-1)], -n, tag)).post();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![marks[0].scaled(1)], 0, tag)).post();
    for i in 0..10 {
        let tag = solver.new_constraint_tag();
        solver.add_constraint(pumpkin_solver::less_than_or_equals(
            vec![marks[i].scaled(1), marks[i + 1].scaled(-1)], -1, tag)).post();
    }
    let mut diffs: Vec<Var> = Vec::new();
    for i in 0..11 {
        for j in (i + 1)..11 {
            let d = solver.new_bounded_integer(1, 200);
            let tag = solver.new_constraint_tag();
            solver.add_constraint(pumpkin_solver::equals(
                vec![marks[j].scaled(1), marks[i].scaled(-1), d.scaled(-1)], 0, tag)).post();
            diffs.push(d);
        }
    }
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(diffs, tag)).post();
    let total = solver.new_bounded_integer(0, 10200);
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(
        vec![x.scaled(1000), marks[10].scaled(1), total.scaled(-1)], 0, tag)).post();
    let mut m = Model::new();
    m.put("x", x);
    m.minimise(total);
    m
}
"""

# minimization_step_one: x = n - 1 is the optimum, and x = n is one above it. The helper
# h = n - x is created after x, and Pumpkin's default search tries h = 0 first, which puts
# x = n as the first improving solution (checked: objectives 2, then the optimum 1).
# A runner that stopped at its first solution would emit n and fail.
STEP_RS = """fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.int("n");
    let x = solver.new_bounded_integer(n - 1, n);
    let h = solver.new_bounded_integer(0, 1);
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![x.scaled(1), h.scaled(1)], n, tag)).post();
    let mut m = Model::new();
    m.put("x", x);
    m.minimise(x);
    m
}
"""

# optimum_enumeration: four values in 0..2 with a sum of at least n; ten optimal tuples.
SUM_RS = """fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.int("n");
    let x: Vec<Var> = (0..4).map(|_| solver.new_bounded_integer(0, 2)).collect();
    let total = solver.new_bounded_integer(0, 8);
    let tag = solver.new_constraint_tag();
    let lower: Vec<Term> = x.iter().map(|&v| v.scaled(-1)).collect();
    solver.add_constraint(pumpkin_solver::less_than_or_equals(lower, -n, tag)).post();
    let tag = solver.new_constraint_tag();
    let mut defining: Vec<Term> = x.iter().map(|&v| v.scaled(1)).collect();
    defining.push(total.scaled(-1));
    solver.add_constraint(pumpkin_solver::equals(defining, 0, tag)).post();
    let mut m = Model::new();
    m.put("x", x);
    m.minimise(total);
    m
}
"""

# output_shapes: a 2x2x2 integer cube and a 2x2 Boolean grid are carried; the
# 30000000002 scalar is beyond Pumpkin's i32 domains and no shape can split it, so build
# refuses it. CONTRACT.md documents the i32 limit.
SHAPES_RS = """fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.int("n");
    let mut cube: Vec<Vec<Vec<Var>>> = Vec::new();
    for _ in 0..2 {
        let mut plane = Vec::new();
        for _ in 0..2 {
            let mut row = Vec::new();
            for _ in 0..2 {
                row.push(solver.new_bounded_integer(0, 10));
            }
            plane.push(row);
        }
        cube.push(plane);
    }
    let mut grid: Vec<Vec<Lit>> = Vec::new();
    for _ in 0..2 {
        let mut row = Vec::new();
        for _ in 0..2 {
            row.push(solver.new_literal());
        }
        grid.push(row);
    }
    for i in 0..2usize {
        for j in 0..2usize {
            for k in 0..2usize {
                let rhs = (i + j + k) as i32 + n;
                let tag = solver.new_constraint_tag();
                solver.add_constraint(pumpkin_solver::equals(vec![cube[i][j][k].scaled(1)], rhs, tag)).post();
            }
        }
    }
    for i in 0..2usize {
        for j in 0..2usize {
            let predicate = if i == j { grid[i][j].get_true_predicate() } else { grid[i][j].get_false_predicate() };
            let tag = solver.new_constraint_tag();
            solver.add_clause(vec![predicate], tag);
        }
    }
    let mut m = Model::new();
    m.put("cube", cube);
    m.put("grid", grid);
    drop(m);
    panic!("output 'big' needs 30000000002, beyond the 32-bit (i32) range of Pumpkin domains")
}
"""

# instance_shapes: ragged rows, rows of mixed types (only the integer column is read) and
# string fields the model never reads.
SHAPED_RS = """fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.int("n");
    let rows = inst.matrix("rows");
    let pairs = inst.get("mixed").as_array().expect("mixed is an array");
    let row_total: i32 = rows.iter().map(|row| row.iter().sum::<i32>()).sum();
    let key_total: i32 = pairs.iter().map(|row| row[0].as_i64().expect("integer") as i32).sum();
    let total = solver.new_bounded_integer(0, 1000);
    let key = solver.new_bounded_integer(0, 1000);
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![total.scaled(1)], n + row_total, tag)).post();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![key.scaled(1)], key_total, tag)).post();
    let mut m = Model::new();
    m.put("total", total);
    m.put("key", key);
    m
}
"""

# error_detail: the instance's optimize field is a Boolean, read as an integer. The
# accessor panics, and the panic names the field.
FAILING_RS = """fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let bound = inst.int("optimize");
    let x = solver.new_bounded_integer(0, bound);
    let mut m = Model::new();
    m.put("x", x);
    m
}
"""

# stray_stdout: the submission logs to stderr. Stdout is the protocol stream, so a
# println! there is the malformed_output case, not this one.
CHATTY_RS = """fn build(inst: &Instance, solver: &mut Solver) -> Model {
    eprintln!("loading the model");
    let n = inst.int("n");
    eprintln!("building for n = {}", n);
    let x = solver.new_bounded_integer(0, n);
    let y = solver.new_bounded_integer(0, n);
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![x.scaled(1), y.scaled(1)], n, tag)).post();
    let mut m = Model::new();
    m.put("x", x);
    m.put("y", y);
    m
}
"""

# auxiliary_free_distinct: a free variable that no declared output mentions.
AUXILIARY_RS = """fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.int("n");
    let x = solver.new_bounded_integer(0, n);
    let y = solver.new_bounded_integer(0, n);
    let _spare = solver.new_bounded_integer(0, 5);
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![x.scaled(1), y.scaled(1)], n, tag)).post();
    let mut m = Model::new();
    m.put("x", x);
    m.put("y", y);
    m
}
"""

# large_model: 3000 0/1 integers in one sum, reported as an output.
LARGE_RS = """fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.int("n");
    let b: Vec<Var> = (0..3000).map(|_| solver.new_bounded_integer(0, 1)).collect();
    let count = solver.new_bounded_integer(0, 3000);
    let mut terms: Vec<Term> = b.iter().map(|&v| v.scaled(1)).collect();
    terms.push(count.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(terms, 0, tag)).post();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![count.scaled(1)], n, tag)).post();
    let mut m = Model::new();
    m.put("b", b);
    m.put("count", count);
    m
}
"""


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

        # Bug-class checks (readiness level 2).
        result = evaluate(candidate("optimization_timeout", UNPROVABLE), "readiness", SOLVER,
                          reference_source=EASY_MIN, execution_timeout=3)
        results["optimization_timeout"] = (result["reason"] == "execution_timeout"
                                           and all(item.get("solutions_received", 0) == 0
                                                   for item in result["instances"]))
        check("minimization_step_one", STEP_RS, reference=STEP_REF)
        result = check("optimum_enumeration", SUM_RS, reference=SUM_REF, solution_limit=3)
        results["optimum_enumeration"] = result["accepted"] and result["solutions_checked"] == 3
        # The i32 refusal is the documented limit, raised by build as an execution_error.
        result = evaluate(candidate("output_shapes", SHAPES_RS), "readiness", SOLVER,
                          reference_source=SHAPES_REF)
        results["output_shapes"] = (result["reason"] == "execution_error"
                                    and "32-bit" in json.dumps(result))
        check("instance_shapes", SHAPED_RS, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        result = evaluate(candidate("error_detail", FAILING_RS), "readiness", SOLVER, reference_source=REFERENCE)
        results["error_detail"] = (result["reason"] == "execution_error"
                                   and "instance field optimize" in json.dumps(result))
        check("stray_stdout", CHATTY_RS)
        result = check("auxiliary_free_distinct", AUXILIARY_RS, solution_limit=3)
        results["auxiliary_free_distinct"] = result["accepted"] and result["solutions_checked"] == 3
        check("large_model", LARGE_RS, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)

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
