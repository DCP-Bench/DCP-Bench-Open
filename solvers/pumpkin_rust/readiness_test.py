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

Two checks deserve a word on what they actually assert. `malformed_output` uses
a submission that writes junk on stdout: the driver owns that stream for the
JSONL protocol, so anything a model prints there corrupts it, and the evaluator
has to reject the run rather than parse around it. `timeout_cleanup` uses an
unsatisfiable pigeonhole rather than a sleep, so it also exercises the path
where Pumpkin itself is still searching when the budget runs out.
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

HEAD = "fn build(inst: &Instance, cp: &mut Cp) -> Model {\n"
TAIL = "}\n"
DECLARE = ("    let n = inst.int(\"n\");\n"
           "    let x = cp.int(0, n);\n"
           "    let y = cp.int(0, n);\n")
EXPORT = ("    let mut m = Model::new();\n"
          "    m.put(\"x\", x);\n"
          "    m.put(\"y\", y);\n")

GOOD = HEAD + DECLARE + "    cp.eq(vec![t(x), t(y)], n);\n" + EXPORT + "    m\n" + TAIL
# `n` is a maximum here, so the objective has room to move in both directions.
OPTIMAL = (HEAD + DECLARE + "    cp.ge(vec![t(x), t(y)], n);\n"
           "    let total = cp.sum(vec![t(x), t(y)]);\n" + EXPORT
           + "    m.DIRECTION(total);\n    m\n" + TAIL)
# Compiles and solves, then corrupts the protocol stream the driver owns.
MALFORMED = (HEAD + DECLARE + "    cp.eq(vec![t(x), t(y)], n);\n"
             "    println!(\"this is not a protocol record\");\n" + EXPORT + "    m\n" + TAIL)
UNSATISFIABLE = (HEAD + DECLARE + "    cp.eq(vec![t(x)], 0);\n    cp.eq(vec![t(x)], 1);\n"
                 + EXPORT + "    m\n" + TAIL)
# 40 pigeons into 39 holes: satisfiable-looking, genuinely unsatisfiable, and
# slow enough that a two-second budget expires inside Pumpkin's search.
SLOW = (HEAD + DECLARE + "    cp.eq(vec![t(x), t(y)], n);\n"
        "    let birds = cp.ints(40, 0, 38);\n"
        "    cp.all_different(terms(&birds));\n" + EXPORT + "    m\n" + TAIL)
UNCOMPILABLE = "this is not Rust\n"

# Rust can inspect its own container, so this check runs through the real
# submission path. A failed probe panics, which run.py reports as an execution
# error, so the check only passes when every probe held.
ISOLATED = '''fn build(inst: &Instance, cp: &mut Cp) -> Model {
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
    let x = cp.int(0, n);
    let y = cp.int(0, n);
    cp.eq(vec![t(x), t(y)], n);
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
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)
        check("compilation_error", UNCOMPILABLE, expected={"compilation_error"})

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
