"""Readiness checks for the pindakaas_rust integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver pindakaas_rust` runs this and keeps
its output as the readiness evidence.

This integration is for satisfaction problems only (`optimization` is false in the
metadata): Pindakaas has no optimiser, and the driver adds none. A submission is one Rust
file spliced into a binary that the image compiles against a prebuilt driver library, so
the integration also has to prove that a submission which does not compile is reported as
`compilation_error`. Every check below pays a real `rustc` invocation.

A few checks deserve a word. `malformed_output` uses a submission that writes junk on
stdout: the driver owns that stream for the JSONL protocol. `timeout_cleanup` uses an
infeasible Golomb ruler rather than a sleep, so the budget expires inside the solver's
search. `unsupported_optimization` hands an optimisation reference a submission that can
only be satisfied, and the evaluator must reject its non-optimal answer. `implied_helper`
enumerates every solution of a conditional constraint over integer variables, because
Pindakaas's own `encode_implied` silently loses solutions there and the helper that
replaces it must not. `overflow_guard` checks that a constraint wide enough to overflow
`i64` panics instead of being dropped.
"""
import json
from pathlib import Path
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "pindakaas_rust"

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

HEAD = "fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {\n"
TAIL = "}\n"
DECLARE = ("    let n = inst.int(\"n\");\n"
           "    let x = IntVar::new(0..=n);\n"
           "    let y = IntVar::new(0..=n);\n")
RETURN_XY = ("    let mut out = Out::new();\n"
             "    out.put(\"x\", &x).put(\"y\", &y);\n"
             "    Ok(out)\n")
SUM_EQ_N = "    post(s, iv(&x) + iv(&y), Comparator::Equal, n)?;\n"

GOOD = HEAD + DECLARE + SUM_EQ_N + RETURN_XY + TAIL
# The reference minimises x + y subject to x + y >= n. This submission is satisfiable but
# only accepts x + y >= n + 1, so every answer it gives is feasible and not optimal.
NOT_OPTIMAL = (HEAD + DECLARE
               + "    post(s, iv(&x) + iv(&y), Comparator::GreaterEq, n + 1)?;\n"
               + RETURN_XY + TAIL)
# Compiles and solves, then corrupts the protocol stream the driver owns.
MALFORMED = (HEAD + DECLARE + SUM_EQ_N
             + "    println!(\"this is not a protocol record\");\n"
             + RETURN_XY + TAIL)
# The two bounds contradict each other: no solution, whether it is found while
# encoding or by search.
UNSATISFIABLE = (HEAD + DECLARE
                 + "    post(s, iv(&x), Comparator::Equal, 0)?;\n"
                 + "    post(s, iv(&x), Comparator::Equal, 1)?;\n"
                 + RETURN_XY + TAIL)
# An 11-mark Golomb ruler within length 71: infeasible (the optimum is 72), and too hard
# to refute in two seconds, so the budget expires inside the solver's search.
SLOW = (HEAD + DECLARE + SUM_EQ_N
        + "    let marks: Vec<IntVar> = (0..11).map(|_| IntVar::new(0..=71)).collect();\n"
        + "    post(s, iv(&marks[0]), Comparator::Equal, 0)?;\n"
        + "    for i in 0..10 {\n"
        + "        post(s, iv(&marks[i + 1]) - iv(&marks[i]), Comparator::GreaterEq, 1)?;\n"
        + "    }\n"
        + "    let mut diffs = Vec::new();\n"
        + "    for i in 0..11 {\n"
        + "        for j in (i + 1)..11 {\n"
        + "            diffs.push(define(s, iv(&marks[j]) - iv(&marks[i]))?);\n"
        + "        }\n"
        + "    }\n"
        + "    all_different(s, &diffs)?;\n"
        + RETURN_XY + TAIL)
UNCOMPILABLE = "this is not Rust\n"

# Rust can inspect its own container, so this check runs through the real
# submission path. A failed probe panics, which the driver reports as an
# execution error, so the check only passes when every probe held.
ISOLATED = '''fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
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
    let x = IntVar::new(0..=n);
    let y = IntVar::new(0..=n);
    post(s, iv(&x) + iv(&y), Comparator::Equal, n)?;
    let mut out = Out::new();
    out.put("x", &x).put("y", &y);
    Ok(out)
}
'''

# ---------------------------------------------------------------------------
# Bug-class checks (readiness level 2). The trusted references below are the
# cpmpy_python ones; each submission is this integration's own Pindakaas form of
# the same model. The optimisation-only checks do not apply: there is no objective.

SHAPES_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
cube = cp.intvar(0, 10, shape=(2, 2, 2), name="cube")
grid = cp.boolvar(shape=(2, 2), name="grid")
model = cp.Model([cube[i, j, k] == i + j + k + n for i in range(2) for j in range(2) for k in range(2)],
                 [grid[i, j] == (i == j) for i in range(2) for j in range(2)])
model.solve()
solution = {"cube": cube.value().tolist(), "grid": grid.value().tolist(), "big": 30000000000 + n}
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
model = cp.Model(cp.sum(b) == n)
model.solve()
solution = {"b": b.value().tolist()}
print(json.dumps(solution))
"""

CONSTANT_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 10, name="x")
model = cp.Model(x == n)
model.solve()
solution = {"x": int(x.value()), "k": 42, "flag": True}
print(json.dumps(solution))
"""

PERMUTATION_REF = """
# Data
n = 4
# End of data
import cpmpy as cp
import json
x = cp.intvar(1, n, shape=n, name="x")
model = cp.Model(cp.AllDifferent(x))
model.solve()
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
"""

IMPLIED_REF = """
# Data
n = 4
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 5, name="x")
y = cp.intvar(0, 5, name="y")
b = cp.boolvar(name="b")
model = cp.Model(b.implies(x + y <= n))
model.solve()
solution = {"x": int(x.value()), "y": int(y.value()), "b": bool(b.value())}
print(json.dumps(solution))
"""

# output_shapes: a 2x2x2 integer cube, a 2x2 Boolean grid and a value beyond 32 bits.
SHAPES_RS = """fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    let mut cube: Vec<Vec<Vec<IntVar>>> = Vec::new();
    for i in 0..2i64 {
        let mut plane = Vec::new();
        for j in 0..2i64 {
            let mut row = Vec::new();
            for k in 0..2i64 {
                let cell = IntVar::new(0..=10);
                post(s, iv(&cell), Comparator::Equal, i + j + k + n)?;
                row.push(cell);
            }
            plane.push(row);
        }
        cube.push(plane);
    }
    let mut grid: Vec<Vec<Lit>> = Vec::new();
    for i in 0..2usize {
        let mut row = Vec::new();
        for j in 0..2usize {
            let cell = s.new_lit();
            s.add_clause([if i == j { cell } else { !cell }])?;
            row.push(cell);
        }
        grid.push(row);
    }
    let mut out = Out::new();
    out.put("cube", cube);
    out.put("grid", grid);
    out.put("big", 30000000000i64 + n);
    Ok(out)
}
"""

# instance_shapes: ragged rows, rows of mixed types (only the integer column is read) and
# string fields the model never reads.
SHAPED_RS = """fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    let rows = inst.matrix("rows");
    let pairs = inst.get("mixed").as_array().expect("mixed is an array");
    let row_total: i64 = rows.iter().map(|row| row.iter().sum::<i64>()).sum();
    let key_total: i64 = pairs.iter().map(|row| row[0].as_i64().expect("integer")).sum();
    let total = IntVar::new(0..=1000);
    let key = IntVar::new(0..=1000);
    post(s, iv(&total), Comparator::Equal, n + row_total)?;
    post(s, iv(&key), Comparator::Equal, key_total)?;
    let mut out = Out::new();
    out.put("total", &total);
    out.put("key", &key);
    Ok(out)
}
"""

# error_detail: the instance's optimize field is a Boolean, read as an integer. The
# accessor panics, and the panic names the field.
FAILING_RS = """fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let bound = inst.int("optimize");
    let x = IntVar::new(0..=bound);
    let _ = s;
    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
"""

# stray_stdout: the submission logs to stderr. Stdout is the protocol stream, so a
# println! there is the malformed_output case, not this one.
CHATTY_RS = (HEAD
             + "    eprintln!(\"loading the model\");\n"
             + DECLARE
             + "    eprintln!(\"building for n = {}\", n);\n"
             + SUM_EQ_N + RETURN_XY + TAIL)

# auxiliary_free_distinct: a free variable that no declared output mentions.
AUXILIARY_RS = (HEAD + DECLARE
                + "    let _spare = IntVar::new(0..=5);\n"
                + "    let _flag = s.new_lit();\n"
                + SUM_EQ_N + RETURN_XY + TAIL)

# large_model: 3000 Booleans in one cardinality constraint, reported as an output.
LARGE_RS = """fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    let b: Vec<Lit> = (0..3000).map(|_| s.new_lit()).collect();
    let mut sum = LinExp::default();
    for l in &b {
        sum += LinExp::from(*l);
    }
    post(s, sum, Comparator::Equal, n)?;
    let mut out = Out::new();
    out.put("b", b);
    Ok(out)
}
"""

# constant_outputs: an integer constant and a Boolean constant declared as outputs.
CONSTANT_RS = """fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    let x = IntVar::new(0..=10);
    post(s, iv(&x), Comparator::Equal, n)?;
    let mut out = Out::new();
    out.put("x", &x).put("k", 42i64).put("flag", true);
    Ok(out)
}
"""

# n_cap: seven solutions for n = 6, so a cap of two must come back exactly two.
N_CAP_REF = REFERENCE.replace("n = 2", "n = 6")

# alldiff_helper: all 24 permutations of four values.
PERMUTATION_RS = """fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    let x: Vec<IntVar> = (0..n).map(|_| IntVar::new(1..=n)).collect();
    all_different(s, &x)?;
    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
"""

# implied_helper: b -> x + y <= n over integer variables, written with the helper. All 36
# pairs stay possible with b false, and 15 satisfy the bound with b true: 51 rows. Pindakaas's
# own encode_implied narrows the domains here and loses solutions.
IMPLIED_RS = """fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    let x = IntVar::new(0..=5);
    let y = IntVar::new(0..=5);
    let b = s.new_lit();
    post_if(s, &[b], iv(&x) + iv(&y), Comparator::LessEq, n)?;
    let mut out = Out::new();
    out.put("x", &x).put("y", &y).put("b", b);
    Ok(out)
}
"""

# overflow_guard: 2^61 * x + 2^61 * y <= 2^62 over 0..4 would overflow i64 inside Pindakaas.
OVERFLOW_RS = (HEAD + DECLARE
               + "    post(s, iv(&x) * (1i64 << 61) + iv(&y) * (1i64 << 61), Comparator::LessEq, 1i64 << 62)?;\n"
               + RETURN_XY + TAIL)


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
        check("unsupported_optimization", NOT_OPTIMAL, reference=OPTIMIZING,
              expected={"suboptimal_solution", "invalid_solution", "wrong_solution"})
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("compilation_error", UNCOMPILABLE, expected={"compilation_error"})

        # The stop must land within a margin of the budget, not merely be reported.
        started = time.monotonic()
        result = evaluate(candidate("timeout_cleanup", SLOW), "readiness", SOLVER,
                          reference_source=REFERENCE, execution_timeout=2)
        results["timeout_cleanup"] = (result["reason"] == "execution_timeout"
                                      and time.monotonic() - started < 40)

        # Bug-class checks (readiness level 2).
        check("output_shapes", SHAPES_RS, reference=SHAPES_REF)
        check("instance_shapes", SHAPED_RS, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        result = evaluate(candidate("error_detail", FAILING_RS), "readiness", SOLVER, reference_source=REFERENCE)
        results["error_detail"] = (result["reason"] == "execution_error"
                                   and "instance field optimize" in json.dumps(result))
        check("stray_stdout", CHATTY_RS)
        result = check("auxiliary_free_distinct", AUXILIARY_RS, solution_limit=3)
        results["auxiliary_free_distinct"] = result["accepted"] and result["solutions_checked"] == 3
        check("large_model", LARGE_RS, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)
        check("constant_outputs", CONSTANT_RS, reference=CONSTANT_REF)
        result = check("n_cap", GOOD, reference=N_CAP_REF, solution_limit=2)
        results["n_cap"] = result["accepted"] and result["solutions_checked"] == 2
        result = check("alldiff_helper", PERMUTATION_RS, reference=PERMUTATION_REF, solution_limit=30)
        results["alldiff_helper"] = result["accepted"] and result["solutions_checked"] == 24
        result = check("implied_helper", IMPLIED_RS, reference=IMPLIED_REF, solution_limit=60)
        results["implied_helper"] = result["accepted"] and result["solutions_checked"] == 51
        result = evaluate(candidate("overflow_guard", OVERFLOW_RS), "readiness", SOLVER, reference_source=REFERENCE)
        results["overflow_guard"] = (result["reason"] == "execution_error"
                                     and "too wide" in json.dumps(result))

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
