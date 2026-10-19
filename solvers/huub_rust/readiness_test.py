"""Readiness checks for the huub_rust integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver huub_rust` runs this and keeps
its output as the readiness evidence.

A submission is one Rust file spliced into a binary that the image compiles
against a prebuilt driver library, so this integration also has to prove that a
submission which does not compile is reported as `compilation_error`. Every check
below pays a real `rustc` invocation.

Three checks deserve a word on what they actually assert. `malformed_output`
uses a submission that writes junk on stdout: the driver owns that stream for
the JSONL protocol, so anything a model prints there corrupts it, and the
evaluator has to reject the run rather than parse around it. `timeout_cleanup`
uses an infeasible Golomb ruler rather than a sleep, so it also exercises the
path where Huub itself is still searching when the budget runs out, and it
checks that the stop lands within a margin of the budget. `unsat_at_lowering`
posts constraints that only conflict once the model is lowered, so both infeasibility
paths are covered.
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

SOLVER = "huub_rust"

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

HEAD = "fn build(inst: &Instance, m: &mut Model) -> Res<Out> {\n"
TAIL = "}\n"
DECLARE = ("    let n = inst.int(\"n\");\n"
           "    let x = m.new_int_decision(0..=n);\n"
           "    let y = m.new_int_decision(0..=n);\n")
RETURN_XY = ("    let mut out = Out::new();\n"
             "    out.put(\"x\", x).put(\"y\", y);\n"
             "    Ok(out)\n")

GOOD = (HEAD + DECLARE
        + "    m.linear(x + y).eq(n).post()?;\n"
        + RETURN_XY + TAIL)
# `n` is a maximum here, so the objective has room to move in both directions.
OPTIMAL = (HEAD + DECLARE
           + "    m.linear(x + y).ge(n).post()?;\n"
           + "    let total = m.new_int_decision(0..=2 * n);\n"
           + "    m.linear(x + y).eq(total).post()?;\n"
           + "    let mut out = Out::new();\n"
           + "    out.put(\"x\", x).put(\"y\", y);\n"
           + "    out.DIRECTION(total);\n"
           + "    Ok(out)\n" + TAIL)
# Compiles and solves, then corrupts the protocol stream the driver owns.
MALFORMED = (HEAD + DECLARE
             + "    m.linear(x + y).eq(n).post()?;\n"
             + "    println!(\"this is not a protocol record\");\n"
             + RETURN_XY + TAIL)
# Conflicts as the second constraint is posted, so `post()` returns Err.
UNSATISFIABLE = (HEAD + DECLARE
                 + "    m.linear(x).eq(0).post()?;\n"
                 + "    m.linear(x).eq(1).post()?;\n"
                 + RETURN_XY + TAIL)
# Every post succeeds; the conflict only shows when the model is lowered.
UNSAT_LOWERING = (HEAD + DECLARE
                  + "    m.linear(x - y).ge(0).post()?;\n"
                  + "    m.linear(x).le(2).post()?;\n"
                  + "    m.linear(y).ge(3).post()?;\n"
                  + RETURN_XY + TAIL)
# An 11-mark Golomb ruler within length 71: infeasible (the optimum is 72), and too
# hard to refute in two seconds, so the budget expires inside Huub's search. A
# pigeonhole would not do: `unique` refutes it while posting.
SLOW = (HEAD + DECLARE
        + "    m.linear(x + y).eq(n).post()?;\n"
        + "    let marks = m.new_int_decisions(11, 0..=71);\n"
        + "    m.linear(marks[0]).eq(0).post()?;\n"
        + "    m.linear(marks[10]).le(71).post()?;\n"
        + "    for i in 0..10 {\n"
        + "        m.linear(marks[i + 1] - marks[i]).ge(1).post()?;\n"
        + "    }\n"
        + "    let mut diffs = Vec::new();\n"
        + "    for i in 0..11 {\n"
        + "        for j in (i + 1)..11 {\n"
        + "            let d = m.new_int_decision(1..=71);\n"
        + "            m.linear(marks[j] - marks[i]).eq(d).post()?;\n"
        + "            diffs.push(d);\n"
        + "        }\n"
        + "    }\n"
        + "    m.unique(diffs).post()?;\n"
        + RETURN_XY + TAIL)
UNCOMPILABLE = "this is not Rust\n"

# Rust can inspect its own container, so this check runs through the real
# submission path. A failed probe panics, which the driver reports as an
# execution error, so the check only passes when every probe held.
ISOLATED = '''fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
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
    let x = m.new_int_decision(0..=n);
    let y = m.new_int_decision(0..=n);
    m.linear(x + y).eq(n).post()?;
    let mut out = Out::new();
    out.put("x", x).put("y", y);
    Ok(out)
}
'''

# ---------------------------------------------------------------------------
# Bug-class checks (readiness level 2). The trusted references below are the
# cpmpy_python ones, copied verbatim; each submission is this integration's own
# Huub form of the same model.

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

OBJ_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(-n, n, name="x")
y = cp.intvar(-n, n, name="y")
model = cp.Model(x + y >= n)
model.DIRECTION(3 * x - 2 * y + 7)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
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

CIRCUIT_REF = """
# Data
n = 5
# End of data
import cpmpy as cp
import json
next = cp.intvar(0, n - 1, shape=n, name="next")
model = cp.Model(cp.Circuit(next))
model.solve()
solution = {"next": next.value().tolist()}
print(json.dumps(solution))
"""

EQ2_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 10**9, name="x")
y = cp.intvar(0, 10**9, name="y")
model = cp.Model(x + y == 2 * n, y == 3 * x)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
"""

# optimization_timeout: the submission adds an unrelated Golomb ruler (11 marks) to its
# objective, so Huub finds a solution at once but cannot prove the optimum in 3 s.
UNPROVABLE = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let x = m.new_int_decision(0..=10);
    m.linear(x).ge(n).post()?;
    let marks = m.new_int_decisions(11, 0..=200);
    m.linear(marks[0]).eq(0).post()?;
    for i in 0..10 {
        m.linear(marks[i + 1] - marks[i]).ge(1).post()?;
    }
    let mut diffs = Vec::new();
    for i in 0..11 {
        for j in (i + 1)..11 {
            let d = m.new_int_decision(1..=200);
            m.linear(marks[j] - marks[i]).eq(d).post()?;
            diffs.push(d);
        }
    }
    m.unique(diffs).post()?;
    let total = m.new_int_decision(0..=10200);
    m.linear(x * 1000 + marks[10]).eq(total).post()?;
    let mut out = Out::new();
    out.put("x", x);
    out.minimise(total);
    Ok(out)
}
"""

# minimization_step_one: x = n - 1 is the optimum, and x = n is one above it. Huub's
# search can reach x = n first, so a runner that stopped at its first solution
# would emit n and fail.
STEP_RS = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let x = m.new_int_decision((n - 1)..=n);
    let h = m.new_int_decision(0..=1);
    m.linear(x + h).eq(n).post()?;
    let mut out = Out::new();
    out.put("x", x);
    out.minimise(x);
    Ok(out)
}
"""

# optimum_enumeration: four values in 0..2 with a sum of at least n; ten optimal tuples.
SUM_RS = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let x = m.new_int_decisions(4, 0..=2);
    let total = m.new_int_decision(0..=8);
    m.linear(x.iter().copied().sum::<IntLinearExp>()).ge(n).post()?;
    m.linear(x.iter().copied().sum::<IntLinearExp>()).eq(total).post()?;
    let mut out = Out::new();
    out.put("x", x);
    out.minimise(total);
    Ok(out)
}
"""

# output_shapes: a 2x2x2 integer cube, a 2x2 Boolean grid and a value beyond 32 bits.
SHAPES_RS = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let mut cube: Vec<Vec<Vec<View<i64>>>> = Vec::new();
    for i in 0..2i64 {
        let mut plane = Vec::new();
        for j in 0..2i64 {
            let mut row = Vec::new();
            for k in 0..2i64 {
                let cell = m.new_int_decision(0..=10);
                m.linear(cell).eq(i + j + k + n).post()?;
                row.push(cell);
            }
            plane.push(row);
        }
        cube.push(plane);
    }
    let never: View<bool> = false.into();
    let mut grid: Vec<Vec<View<bool>>> = Vec::new();
    for i in 0..2usize {
        let mut row = Vec::new();
        for j in 0..2usize {
            let cell = m.new_bool_decision();
            if i == j {
                m.proposition(BoolFormula::Atom(cell)).post()?;
            } else {
                m.proposition(BoolFormula::Implies(
                    Box::new(BoolFormula::Atom(cell)),
                    Box::new(BoolFormula::Atom(never)),
                ))
                .post()?;
            }
            row.push(cell);
        }
        grid.push(row);
    }
    let big = m.new_int_decision(0..=40000000000);
    m.linear(big).eq(30000000000 + n).post()?;
    let mut out = Out::new();
    out.put("cube", cube);
    out.put("grid", grid);
    out.put("big", big);
    Ok(out)
}
"""

# instance_shapes: ragged rows, rows of mixed types (only the integer column is read) and
# string fields the model never reads.
SHAPED_RS = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let rows = inst.matrix("rows");
    let pairs = inst.get("mixed").as_array().expect("mixed is an array");
    let row_total: i64 = rows.iter().map(|row| row.iter().sum::<i64>()).sum();
    let key_total: i64 = pairs.iter().map(|row| row[0].as_i64().expect("integer")).sum();
    let total = m.new_int_decision(0..=1000);
    let key = m.new_int_decision(0..=1000);
    m.linear(total).eq(n + row_total).post()?;
    m.linear(key).eq(key_total).post()?;
    let mut out = Out::new();
    out.put("total", total);
    out.put("key", key);
    Ok(out)
}
"""

# error_detail: the instance's optimize field is a Boolean, read as an integer. The
# accessor panics, and the panic names the field.
FAILING_RS = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let bound = inst.int("optimize");
    let x = m.new_int_decision(0..=bound);
    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
"""

# stray_stdout: the submission logs to stderr. Stdout is the protocol stream, so a
# println! there is the malformed_output case, not this one.
CHATTY_RS = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    eprintln!("loading the model");
    let n = inst.int("n");
    eprintln!("building for n = {}", n);
    let x = m.new_int_decision(0..=n);
    let y = m.new_int_decision(0..=n);
    m.linear(x + y).eq(n).post()?;
    let mut out = Out::new();
    out.put("x", x).put("y", y);
    Ok(out)
}
"""

# auxiliary_free_distinct: a free variable that no declared output mentions.
AUXILIARY_RS = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let x = m.new_int_decision(0..=n);
    let y = m.new_int_decision(0..=n);
    let _spare = m.new_int_decision(0..=5);
    m.linear(x + y).eq(n).post()?;
    let mut out = Out::new();
    out.put("x", x).put("y", y);
    Ok(out)
}
"""

# large_model: 3000 0/1 integers in one sum, reported as an output.
LARGE_RS = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let b = m.new_int_decisions(3000, 0..=1);
    let count = m.new_int_decision(0..=3000);
    m.linear(b.iter().copied().sum::<IntLinearExp>()).eq(count).post()?;
    m.linear(count).eq(n).post()?;
    let mut out = Out::new();
    out.put("b", b);
    out.put("count", count);
    Ok(out)
}
"""

# objective_expression: an objective with an offset and negative terms, minimised over
# variables that take negative values.
OBJECTIVE_MIN_RS = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let x = m.new_int_decision(-n..=n);
    let y = m.new_int_decision(-n..=n);
    m.linear(x + y).ge(n).post()?;
    let obj = m.new_int_decision(-1000..=1000);
    m.linear(x * 3 - y * 2 + 7).eq(obj).post()?;
    let mut out = Out::new();
    out.put("x", x).put("y", y);
    out.minimise(obj);
    Ok(out)
}
"""

OBJECTIVE_MAX_RS = OBJECTIVE_MIN_RS.replace("out.minimise(obj)", "out.maximise(obj)")

# constant_outputs: an integer constant and a Boolean constant declared as outputs.
CONSTANT_RS = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let x = m.new_int_decision(0..=10);
    m.linear(x).eq(n).post()?;
    let mut out = Out::new();
    out.put("x", x).put("k", 42i64).put("flag", true);
    Ok(out)
}
"""

# n_cap: seven solutions for n = 6, so a cap of two must come back exactly two.
N_CAP_REF = REFERENCE.replace("n = 2", "n = 6")

# circuit_helper: the harness's circuit decomposition on five nodes (24 tours).
CIRCUIT_RS = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let next = m.new_int_decisions(n, 0..=(n as i64 - 1));
    circuit(m, &next)?;
    let mut out = Out::new();
    out.put("next", next);
    Ok(out)
}
"""

# eq2_helper: two equalities over the same pair with a coefficient of 3, on domains of
# 10^9. Posted as bounds, these solve; as plain equalities they hang or exhaust memory.
EQ2_RS = """fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let x = m.new_int_decision(0..=1_000_000_000);
    let y = m.new_int_decision(0..=1_000_000_000);
    eq2(m, x + y, 2 * n)?;
    eq2(m, y - x * 3, 0)?;
    let mut out = Out::new();
    out.put("x", x).put("y", y);
    Ok(out)
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
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("unsat_at_lowering", UNSAT_LOWERING, expected={"no_solution"})
        check("compilation_error", UNCOMPILABLE, expected={"compilation_error"})

        # The stop must land within a margin of the budget, not merely be reported.
        started = time.monotonic()
        result = evaluate(candidate("timeout_cleanup", SLOW), "readiness", SOLVER,
                          reference_source=REFERENCE, execution_timeout=2)
        results["timeout_cleanup"] = (result["reason"] == "execution_timeout"
                                      and time.monotonic() - started < 15)

        # Bug-class checks (readiness level 2).
        result = evaluate(candidate("optimization_timeout", UNPROVABLE), "readiness", SOLVER,
                          reference_source=EASY_MIN, execution_timeout=3)
        results["optimization_timeout"] = (result["reason"] == "execution_timeout"
                                           and all(item.get("solutions_received", 0) == 0
                                                   for item in result["instances"]))
        check("minimization_step_one", STEP_RS, reference=STEP_REF)
        result = check("optimum_enumeration", SUM_RS, reference=SUM_REF, solution_limit=3)
        results["optimum_enumeration"] = result["accepted"] and result["solutions_checked"] == 3
        check("output_shapes", SHAPES_RS, reference=SHAPES_REF)
        check("instance_shapes", SHAPED_RS, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        result = evaluate(candidate("error_detail", FAILING_RS), "readiness", SOLVER, reference_source=REFERENCE)
        results["error_detail"] = (result["reason"] == "execution_error"
                                   and "instance field optimize" in json.dumps(result))
        check("stray_stdout", CHATTY_RS)
        result = check("auxiliary_free_distinct", AUXILIARY_RS, solution_limit=3)
        results["auxiliary_free_distinct"] = result["accepted"] and result["solutions_checked"] == 3
        check("large_model", LARGE_RS, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)
        check("objective_expression", OBJECTIVE_MIN_RS, reference=OBJ_REF.replace("DIRECTION", "minimize"))
        check("maximize_expression", OBJECTIVE_MAX_RS, reference=OBJ_REF.replace("DIRECTION", "maximize"))
        check("constant_outputs", CONSTANT_RS, reference=CONSTANT_REF)
        result = check("n_cap", GOOD, reference=N_CAP_REF, solution_limit=2)
        results["n_cap"] = result["accepted"] and result["solutions_checked"] == 2
        check("circuit_helper", CIRCUIT_RS, reference=CIRCUIT_REF, solution_limit=3)
        check("eq2_helper", EQ2_RS, reference=EQ2_REF)

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
