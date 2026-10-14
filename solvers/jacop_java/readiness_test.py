"""Readiness checks for the jacop_java integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver jacop_java` runs this and keeps
its output as the readiness evidence.

A submission is one Java file declaring `class Submission` with
`static Model build(JSONObject instance, Store store)`, compiled in the image
against JaCoP, org.json and the harness jar, so this integration also has to
prove that a submission which does not compile is reported as
`compilation_error`. Every check below pays a real `javac` invocation.

What some checks actually assert. `malformed_output` returns a model that
declares no outputs, which the harness must refuse rather than emit `{}` as a
solution. `stdout_is_log` prints on `System.out` during `build`: the harness
points that stream at stderr, so the run must still be accepted.
`timeout_cleanup` uses an unsatisfiable pigeonhole rather than a sleep, so it
exercises the path where JaCoP itself is still searching when the budget runs
out. `minimization` and `maximization` ask for three solutions, so they also
check that the objective stays fixed at the optimum while enumerating: JaCoP
loses a constraint imposed between searches unless it is propagated at the
base level first, and these checks caught exactly that. `enumeration` asks for more solutions than exist, so it passes only if
the harness blocks on the declared outputs and reports exhaustion.
`partial_search` labels only one variable through `Model.search`; the harness
must still label the rest, or `y` would be emitted unfixed. `native_api`
checks that the store a submission is handed is JaCoP's own.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "jacop_java"

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

HEAD = ("import org.jacop.core.*;\n"
        "import org.jacop.constraints.*;\n"
        "import org.jacop.search.*;\n"
        "import org.json.JSONObject;\n"
        "import dcp.jacop.Model;\n\n"
        "public class Submission {\n"
        "    public static Model build(JSONObject inst, Store store) {\n"
        "        int n = inst.getInt(\"n\");\n"
        "        IntVar x = new IntVar(store, \"x\", 0, n);\n"
        "        IntVar y = new IntVar(store, \"y\", 0, n);\n")
TAIL = "    }\n}\n"
EXPORT = "        Model m = new Model().put(\"x\", x).put(\"y\", y);\n"

GOOD = (HEAD + "        store.impose(new XplusYeqC(x, y, n));\n"
        + EXPORT + "        return m;\n" + TAIL)
# `n` is a lower bound here, so the objective has room to move both ways.
OPTIMAL = (HEAD + "        store.impose(new XplusYgtC(x, y, n - 1));\n"
           + "        IntVar total = new IntVar(store, \"total\", 0, 2 * n);\n"
           + "        store.impose(new XplusYeqZ(x, y, total));\n"
           + EXPORT + "        return m.DIRECTION(total);\n" + TAIL)
MALFORMED = (HEAD + "        store.impose(new XplusYeqC(x, y, n));\n"
             + "        return new Model();\n" + TAIL)
NOISY = (HEAD + "        System.out.println(\"this is not a protocol record\");\n"
         + "        store.impose(new XplusYeqC(x, y, n));\n"
         + EXPORT + "        return m;\n" + TAIL)
UNSATISFIABLE = (HEAD + "        store.impose(new XeqC(x, 0));\n"
                 + "        store.impose(new XeqC(x, 1));\n"
                 + EXPORT + "        return m;\n" + TAIL)
# 40 pigeons into 39 holes with pairwise disequalities: no propagation proves
# it, so a two-second budget expires inside JaCoP's search.
SLOW = (HEAD + "        store.impose(new XplusYeqC(x, y, n));\n"
        + "        IntVar[] birds = new IntVar[40];\n"
        + "        for (int i = 0; i < 40; i++) birds[i] = new IntVar(store, 0, 38);\n"
        + "        for (int i = 0; i < 40; i++)\n"
        + "            for (int j = i + 1; j < 40; j++) store.impose(new XneqY(birds[i], birds[j]));\n"
        + EXPORT + "        return m;\n" + TAIL)
UNCOMPILABLE = "this is not Java\n"
PARTIAL = (HEAD + "        store.impose(new XplusYeqC(x, y, n));\n"
           + EXPORT
           + "        return m.search(new IntVar[]{x}, null, new IndomainMax<IntVar>());\n" + TAIL)

# Java can inspect its own container, so this check runs through the real
# submission path. A failed probe throws, which the harness reports as an
# error, so the check only passes when every probe held.
ISOLATED = '''import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.file.*;
import java.util.*;
import org.jacop.core.*;
import org.jacop.constraints.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    static void require(boolean ok, String what) {
        if (!ok) throw new IllegalStateException(what);
    }

    public static Model build(JSONObject inst, Store store) throws Exception {
        String status = Files.readString(Path.of("/proc/self/status"));
        String uid = status.lines().filter(l -> l.startsWith("Uid:")).findFirst().orElseThrow()
            .trim().split("\\\\s+")[1];
        require(!uid.equals("0"), "container runs as root");
        require(!Files.exists(Path.of("/dataset")), "dataset is visible to the candidate");
        Set<String> entries = new TreeSet<>();
        try (var listing = Files.list(Path.of("/input"))) {
            listing.forEach(p -> entries.add(p.getFileName().toString()));
        }
        require(entries.equals(new TreeSet<>(List.of("model.java", "request.json"))), "unexpected /input " + entries);
        boolean writable;
        try {
            Files.writeString(Path.of("/input/written"), "x");
            writable = true;
        } catch (Exception error) {
            writable = false;
        }
        require(!writable, "input is writable");
        boolean reachable;
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress("1.1.1.1", 443), 500);
            reachable = true;
        } catch (Exception error) {
            reachable = false;
        }
        require(!reachable, "network reachable");

        int n = inst.getInt("n");
        IntVar x = new IntVar(store, "x", 0, n);
        IntVar y = new IntVar(store, "y", 0, n);
        store.impose(new XplusYeqC(x, y, n));
        return new Model().put("x", x).put("y", y);
    }
}
'''

# The harness must hand over JaCoP's own Store and wrap none of its API:
# constraints here are JaCoP global and decomposed constraints.
NATIVE = (HEAD
          + "        org.jacop.core.Store own = store;\n"
          + "        own.impose(new LinearInt(new IntVar[]{x, y}, new int[]{1, 1}, \"==\", n));\n"
          + "        IntVar[] spare = new IntVar[3];\n"
          + "        for (int i = 0; i < 3; i++) spare[i] = new IntVar(own, 1, 3);\n"
          + "        own.impose(new Alldifferent(spare));\n"
          + "        BooleanVar flag = new BooleanVar(own);\n"
          + "        own.impose(new Reified(new XeqC(x, 0), flag));\n"
          + EXPORT + "        return m;\n" + TAIL)


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / f"{name}.java"
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, **kwargs):
            result = evaluate(candidate(name, source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            if not results[name]:
                print(f"{name}: {result.get('reason')} {result.get('detail')}", file=sys.stderr)
            return result

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        enumerated = check("enumeration", GOOD, solution_limit=5)
        # Three solutions exist; anything else means duplicates or a missed one.
        counts = [item.get("solutions_checked") for item in enumerated.get("instances", [])]
        results["enumeration"] = results["enumeration"] and counts == [3]
        if counts != [3]:
            print(f"enumeration: solutions checked per instance {counts}, expected [3]", file=sys.stderr)
        check("minimization", OPTIMAL.replace("DIRECTION", "minimize"), reference=OPTIMIZING, solution_limit=3)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximize"), reference=MAXIMIZING, solution_limit=3)
        check("native_api", NATIVE)
        check("stdout_is_log", NOISY)
        check("partial_search", PARTIAL, solution_limit=5)
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
