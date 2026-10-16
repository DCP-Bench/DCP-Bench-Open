"""Readiness checks for the choco_java integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver choco_java` runs this and keeps
its output as the readiness evidence.

Every submission is one Java file declaring public class Submission with a
static build(Instance, Model, Outputs). The image compiles it against the driver.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "choco_java"

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
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''
OPTIMIZING = REFERENCE.replace("optimize = False", "optimize = True")
MAXIMIZING = OPTIMIZING.replace("model.minimize", "model.maximize")
FLAG_REFERENCE = REFERENCE.replace(
    'solution = {"x": int(x.value()), "y": int(y.value())}',
    'solution = {"x": int(x.value()), "y": int(y.value()), "flag": bool(x.value() == 0)}')
CONSTANT_REFERENCE = REFERENCE.replace(
    'solution = {"x": int(x.value()), "y": int(y.value())}',
    'solution = {"x": int(x.value()), "y": int(y.value()), "k": 5}')
MATRIX_REFERENCE = REFERENCE.replace(
    'solution = {"x": int(x.value()), "y": int(y.value())}',
    'solution = {"x": int(x.value()), "y": int(y.value()), '
    '"m": [[int(x.value()), int(y.value())], [int(y.value()), int(x.value())]]}')
NESTED_REFERENCE = REFERENCE.replace(
    'solution = {"x": int(x.value()), "y": int(y.value())}',
    'solution = {"x": int(x.value()), "y": int(y.value()), '
    '"cube": [[[int(x.value()), int(y.value())], [int(y.value()), int(x.value())]]], '
    '"flags": [[bool(x.value() == 0), bool(y.value() == 0)]], '
    '"big": 30000000000 + 10 * int(x.value()) + int(y.value())}')

# Shared model text. Every model declares x and y as outputs, so each one
# matches the reference's output names.
HEAD = '''import org.chocosolver.solver.Model;
import org.chocosolver.solver.SettingsBuilder;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    IntVar x = m.intVar("x", 0, n);
    IntVar y = m.intVar("y", 0, n);
'''
OUTPUTS = '''    out.put("x", x);
    out.put("y", y);
'''
CLOSE = '''  }
}
'''
EQUAL = '    m.arithm(x, "+", y, "=", n).post();\n'


def optimal(direction, search=""):
    # Minimize or maximize x+y with x+y >= n. The objective is an auxiliary
    # variable that the model never branches on.
    return (HEAD + '    m.arithm(x, "+", y, ">=", n).post();\n'
            "    IntVar total = m.intVar(\"total\", 0, 2 * n);\n"
            '    m.sum(new IntVar[]{x, y}, "=", total).post();\n'
            f"    m.setObjective(Model.{direction}, total);\n" + search + OUTPUTS + CLOSE)


GOOD = HEAD + EQUAL + OUTPUTS + CLOSE
OPTIMAL_MIN = optimal("MINIMIZE")
OPTIMAL_MAX = optimal("MAXIMIZE")
# Upper-bound-first search: the first solution (x=2, y=2, total 4) is far from
# the optimum 2, so the driver has to keep improving.
FROM_ABOVE = optimal("MINIMIZE", "    m.getSolver().setSearch(Search.inputOrderUBSearch(x, y));\n")
# Luby restarts with a learning-based heuristic. Optimality must still be proven.
RESTARTS = optimal("MINIMIZE", "    m.getSolver().setSearch(Search.domOverWDegSearch(x, y));\n"
                               "    m.getSolver().setLubyRestart(2, new FailCounter(m, 2), 1000);\n")
# Lazy clause generation, turned on through the settings hook, for both the
# optimum and the enumeration of the other optima after a reset.
LCG = OPTIMAL_MIN.replace("public class Submission {\n",
                          "public class Submission {\n"
                          "  public static SettingsBuilder settings() { return SettingsBuilder.init().setLCG(true); }\n")
LCG_ENUMERATION = GOOD.replace("public class Submission {\n",
                               "public class Submission {\n"
                               "  public static SettingsBuilder settings() { return SettingsBuilder.init().setLCG(true); }\n")
# A free variable outside the outputs: repeats on x, y must not be counted.
FREE_AUX = HEAD + EQUAL + '    IntVar unused = m.intVar("unused", 0, 5);\n' + OUTPUTS + CLOSE
UNSATISFIABLE = (HEAD + '    m.arithm(x, "=", 0).post();\n    m.arithm(x, "=", 1).post();\n'
                 + OUTPUTS + CLOSE)
# Compiles and solves, but declares no outputs: the driver must reject it.
MALFORMED = HEAD + EQUAL + CLOSE
# Pigeonhole, 20 pigeons and 19 holes, with pairwise disequalities only, so no
# propagator sees the whole and the search outlasts any budget.
PIGEONS = '''    IntVar[] p = m.intVarArray("p", 20, 0, HOLES);
    for (int i = 0; i < 20; i++)
      for (int j = i + 1; j < 20; j++) m.arithm(p[i], "!=", p[j]).post();
'''
SLOW = HEAD + EQUAL + PIGEONS.replace("HOLES", "18") + OUTPUTS + CLOSE
# Solutions come fast but the optimum needs the pigeonhole proof. The driver
# must report a timeout and emit nothing unproven.
OPTIMUM_UNPROVEN = (HEAD + EQUAL + PIGEONS.replace("HOLES", "19")
                    + '    IntVar top = m.intVar("top", 0, 19);\n'
                    + '    m.max(top, p).post();\n'
                    + "    m.setObjective(Model.MINIMIZE, top);\n"
                    + "    m.getSolver().setSearch(Search.inputOrderLBSearch(p));\n"
                    + OUTPUTS + CLOSE)
UNCOMPILABLE = "this is not Java\n"
MATRIX = HEAD + EQUAL + '    out.put("m", new IntVar[][]{{x, y}, {y, x}});\n' + OUTPUTS + CLOSE
# A Boolean output, reified from an integer comparison.
BOOL_OUTPUT = HEAD + EQUAL + '    out.put("flag", m.arithm(x, "=", 0).reify());\n' + OUTPUTS + CLOSE
CONSTANT_OUTPUT = HEAD + EQUAL + '    out.put("k", 5);\n' + OUTPUTS + CLOSE
# Outputs three levels deep, a Boolean matrix as a List, and a number above
# the IntVar range given by its digits.
NESTED = (HEAD + EQUAL
          + "    IntVar[] digits = new IntVar[11];\n"
          + "    digits[0] = m.intVar(3);\n"
          + "    for (int i = 1; i < 9; i++) digits[i] = m.intVar(0);\n"
          + "    digits[9] = x;\n    digits[10] = y;\n"
          + '    out.put("cube", new IntVar[][][]{{{x, y}, {y, x}}});\n'
          + '    out.put("flags", java.util.List.of((Object) new BoolVar[]{m.arithm(x, "=", 0).reify(), m.arithm(y, "=", 0).reify()}));\n'
          + '    out.putDigits("big", digits, 10);\n'
          + OUTPUTS + CLOSE)
# Global constraints and the expression API on the native Model.
NATIVE = (HEAD + "    IntVar[] v = m.intVarArray(\"v\", 3, 0, 2);\n"
          + "    m.allDifferent(v).post();\n"
          + "    m.element(x, new int[]{0, 1, 2}, v[0]).post();\n"
          + "    x.add(y).eq(n).post();\n"
          + "    m.ifThen(m.arithm(x, \">\", 0), m.arithm(v[1], \"=\", 0));\n"
          + OUTPUTS + CLOSE)
# An exception raised by the model must come back as an execution error.
THROWS = HEAD + EQUAL + '    if (n > 0) throw new IllegalStateException("model refused the instance");\n' + OUTPUTS + CLOSE
# A heap the size of the container: the driver must report the JVM's own
# OutOfMemoryError as an error, not wait for a timeout.
HOG = (HEAD + EQUAL + "    java.util.List<long[]> hog = new java.util.ArrayList<>();\n"
       "    while (true) hog.add(new long[10_000_000]);\n  }\n}\n")
# Probes run in build(). A failed probe throws, and the driver reports an
# execution error, so the check passes only when every probe held.
ISOLATED = '''import java.io.File;
import java.io.FileOutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.Set;
import java.util.TreeSet;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  static boolean reachable() {
    try (Socket socket = new Socket()) {
      socket.connect(new InetSocketAddress("1.1.1.1", 443), 500);
      return true;
    } catch (Exception error) {
      return false;
    }
  }

  static void probe() {
    if (System.getProperty("user.name").equals("root")) throw new IllegalStateException("container runs as root");
    if (new File("/dataset").exists()) throw new IllegalStateException("dataset is visible to the candidate");
    Set<String> entries = new TreeSet<>(java.util.Arrays.asList(new File("/input").list()));
    if (!entries.equals(new TreeSet<>(Set.of("model.java", "request.json"))))
      throw new IllegalStateException("unexpected /input: " + entries);
    try (FileOutputStream written = new FileOutputStream("/input/written")) {
      throw new IllegalStateException("input is writable");
    } catch (java.io.IOException expected) {
    }
    if (reachable()) throw new IllegalStateException("network reachable");
  }

  public static void build(Instance inst, Model m, Outputs out) {
    probe();
    int n = inst.getInt("n");
    IntVar x = m.intVar("x", 0, n);
    IntVar y = m.intVar("y", 0, n);
    m.arithm(x, "+", y, "=", n).post();
    out.put("x", x);
    out.put("y", y);
  }
}
'''


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / f"{name}.java"
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, detail=None, **kwargs):
            result = evaluate(candidate(name, source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            ok = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            if ok and detail is not None:
                ok = detail in json.dumps(result)
            results[name] = ok
            if not ok:
                print(name, json.dumps(result)[:2000], file=sys.stderr)
            return result

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL_MIN, reference=OPTIMIZING)
        check("maximization", OPTIMAL_MAX, reference=MAXIMIZING)
        check("optimum_enumeration", OPTIMAL_MIN, reference=OPTIMIZING, solution_limit=3)
        check("optimum_from_above", FROM_ABOVE, reference=OPTIMIZING, solution_limit=1)
        check("restarts", RESTARTS, reference=OPTIMIZING, solution_limit=3)
        check("lcg_optimization", LCG, reference=OPTIMIZING, solution_limit=3)
        check("lcg_enumeration", LCG_ENUMERATION, solution_limit=3)
        check("free_auxiliary", FREE_AUX, solution_limit=3)
        check("native_api", NATIVE)
        check("bool_output", BOOL_OUTPUT, reference=FLAG_REFERENCE, solution_limit=2)
        check("constant_output", CONSTANT_OUTPUT, reference=CONSTANT_REFERENCE)
        check("matrix_output", MATRIX, reference=MATRIX_REFERENCE, solution_limit=3)
        check("nested_outputs", NESTED, reference=NESTED_REFERENCE, solution_limit=3)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("model_exception", THROWS, expected={"execution_error"}, detail="model refused the instance")
        check("out_of_memory", HOG, expected={"execution_error"}, detail="OutOfMemoryError")
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=3)
        check("optimum_unproven_timeout", OPTIMUM_UNPROVEN, expected={"execution_timeout"}, execution_timeout=4)
        check("compilation_error", UNCOMPILABLE, expected={"compilation_error"}, detail="not Java")

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
