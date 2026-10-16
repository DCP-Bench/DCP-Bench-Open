"""Readiness checks for the maxicp_java integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver maxicp_java` runs this and keeps
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

SOLVER = "maxicp_java"

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

# Reference for the Java model below: the outputs keep the names x and y.
# Every model declares x and y as outputs, so each one matches the reference's
# output names.
HEAD = '''import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    CPIntVar x = m.intVar(0, n);
    CPIntVar y = m.intVar(0, n);
'''
OUTPUTS = '''    out.put("x", x);
    out.put("y", y);
'''
CLOSE = '''  }
}
'''
EQUAL = '    m.cp().post(eq(sum(x, y), n));\n'
GOOD = HEAD + EQUAL + OUTPUTS + CLOSE


def optimal(direction, extra=""):
    # Minimise or maximise x+y with x+y >= n. The objective is a view over x and y.
    return (HEAD + '    m.cp().post(ge(sum(x, y), n));\n'
            f"    m.{direction}(sum(x, y));\n" + extra + OUTPUTS + CLOSE)


OPTIMAL_MIN = optimal("minimize")
OPTIMAL_MAX = optimal("maximize")
# Optimisation with the instance flag toggled by the tests that need both forms.
OPTIMAL_FLAG = (HEAD + '    if (inst.getBool("optimize")) {\n'
                '      m.cp().post(ge(sum(x, y), n));\n'
                '      m.minimize(sum(x, y));\n'
                '    } else {\n'
                '      m.cp().post(eq(sum(x, y), n));\n'
                '    }\n' + OUTPUTS + CLOSE)
# Lazy objective: a variable carrying the objective, branched on by the driver.
# Free auxiliary: a variable outside the outputs; repeats on x, y must not count.
FREE_AUX = HEAD + EQUAL + '    CPIntVar unused = m.intVar(0, 5);\n' + OUTPUTS + CLOSE
UNSATISFIABLE = (HEAD + '    m.cp().post(eq(x, 0));\n    m.cp().post(eq(x, 1));\n' + OUTPUTS + CLOSE)
# Compiles and solves, but declares no outputs: the driver must reject it.
MALFORMED = HEAD + EQUAL + CLOSE
# Pigeonhole, 20 pigeons and 18 holes, with pairwise disequalities only, so no
# propagator sees the whole and the search outlasts any budget.
SLOW = (HEAD + EQUAL
        + "    CPIntVar[] p = m.intVarArray(20, 0, 17);\n"
        + "    for (int i = 0; i < 20; i++)\n"
        + "      for (int j = i + 1; j < 20; j++) m.cp().post(neq(p[i], p[j]));\n"
        + '    out.put("p", p);\n' + OUTPUTS + CLOSE)
UNCOMPILABLE = "this is not Java\n"
# Outputs three levels deep, a Boolean matrix and a value beyond 32 bits given by its digits.
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
SHAPES = HEAD.replace("    CPIntVar x = m.intVar(0, n);\n    CPIntVar y = m.intVar(0, n);\n", "") + (
    "    CPIntVar[][][] cube = new CPIntVar[2][2][2];\n"
    "    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) for (int k = 0; k < 2; k++) {\n"
    "      cube[i][j][k] = m.intVar(0, 10);\n"
    "      m.cp().post(eq(cube[i][j][k], i + j + k + n));\n"
    "    }\n"
    "    CPBoolVar[][] grid = new CPBoolVar[2][2];\n"
    "    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) {\n"
    "      grid[i][j] = m.boolVar();\n"
    "      m.cp().post(eq(grid[i][j], i == j ? 1 : 0));\n"
    "    }\n"
    "    CPIntVar[] digits = new CPIntVar[11];\n"
    "    digits[0] = m.intVar(3, 3);\n"
    "    for (int i = 1; i < 10; i++) digits[i] = m.intVar(0, 0);\n"
    "    digits[10] = m.intVar(n, n);\n"
    '    out.put("cube", cube);\n'
    '    out.put("grid", grid);\n'
    '    out.putDigits("big", digits, 10);\n'
    + CLOSE)
# instance_shapes: ragged rows, rows of mixed types, a string field the model ignores,
# and name/note keys, on two instances with different shapes.
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
SHAPED = '''import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int[][] rows = inst.getIntMatrix("rows");
    int rowTotal = 0;
    for (int[] row : rows) for (int v : row) rowTotal += v;
    JsonArray mixed = inst.raw("mixed").getAsJsonArray();
    int key = 0;
    for (JsonElement row : mixed) key += row.getAsJsonArray().get(0).getAsInt();
    CPIntVar total = m.intVar(0, 1000);
    m.cp().post(eq(total, n + rowTotal));
    CPIntVar keyVar = m.intVar(0, 1000);
    m.cp().post(eq(keyVar, key));
    out.put("total", total);
    out.put("key", keyVar);
  }
}
'''
# error_detail: the solver refuses an empty domain while the model is built; the
# evaluator must report execution_error with the library's own message.
FAILING = HEAD + "    out.put(\"x\", CPFactory.makeIntVar(m.cp(), 3, 1));\n" + CLOSE
# stray_stdout: the model prints; the protocol stream must survive it.
CHATTY = HEAD.replace("    int n", '    System.out.println("building for n = " + inst.getInt("n"));\n    int n') + EQUAL + OUTPUTS + CLOSE
# optimum_enumeration: a compound objective (a sum) with ten optimal solutions.
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
SUM = ('''import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    CPIntVar[] x = m.intVarArray(4, 0, 2);
    CPIntVar total = sum(x);
    m.cp().post(ge(total, n));
    m.minimize(total);
    out.put("x", x);
  }
}
''')
# minimization_step_one: the first solution the driver's branching reaches is
# optimum + 1 (x = 0 gives 10, the optimum 9 sits at x = 1). An off-by-one bound
# would stop at 10 and report that as optimal.
STEP_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 10, name="x")
model = cp.Model(x <= n - 1)
model.minimize(10 - x)
model.solve()
solution = {"x": int(x.value())}
print(json.dumps(solution))
"""
STEP = ('''import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    CPIntVar x = m.intVar(0, 10);
    m.cp().post(le(x, n - 1));
    m.minimize(plus(minus(x), 10));
    out.put("x", x);
  }
}
''')
# optimization_timeout: an easy reference (x >= n, minimise x). The submission
# adds an unrelated hard part to its objective (a Golomb ruler of 11 marks) so the
# solver finds a solution fast but cannot prove it within a 3 s budget.
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
UNPROVABLE = ('''import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    CPIntVar x = m.intVar(0, 10);
    m.cp().post(ge(x, n));
    CPIntVar[] marks = m.intVarArray(11, 0, 200);
    m.cp().post(eq(marks[0], 0));
    for (int i = 0; i < 10; i++) m.cp().post(lt(marks[i], marks[i + 1]));
    CPIntVar[] diffs = new CPIntVar[55];
    int k = 0;
    for (int i = 0; i < 11; i++)
      for (int j = i + 1; j < 11; j++) {
        CPIntVar d = m.intVar(0, 200);
        m.cp().post(sum(new CPIntVar[]{marks[j], minus(marks[i])}, d));
        diffs[k++] = d;
      }
    m.cp().post(allDifferent(diffs));
    m.minimize(sum(mul(x, 1000), marks[10]));
    out.put("x", x);
  }
}
''')
# auxiliary_free_distinct: a registered free variable repeats each (x, y) six times.
AUXILIARY = FREE_AUX
# large_model: 3000 Booleans in one sum, reported as an output.
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
LARGE = ('''import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    CPBoolVar[] b = m.boolVarArray(3000);
    CPIntVar count = m.intVar(0, 3000);
    m.cp().post(eq(count, sum(b)));
    m.cp().post(eq(count, n));
    out.put("b", b);
    out.put("count", count);
  }
}
''')
# Probes run in build(). A failed probe throws, and the driver reports an
# execution error, so the check passes only when every probe held.
ISOLATED = '''import java.io.File;
import java.io.FileOutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.Set;
import java.util.TreeSet;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
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
    CPIntVar x = m.intVar(0, n);
    CPIntVar y = m.intVar(0, n);
    m.cp().post(eq(sum(x, y), n));
    out.put("x", x);
    out.put("y", y);
  }
}
'''
# A heap the size of the container: the driver must report the JVM's own
# OutOfMemoryError as an error, not wait for a timeout.
HOG = (HEAD + EQUAL + "    java.util.List<long[]> hog = new java.util.ArrayList<>();\n"
       "    while (true) hog.add(new long[10_000_000]);\n  }\n}\n")


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
        check("changed_instances", OPTIMAL_FLAG, reference=OPTIMIZING, instances=[{"n": 3, "optimize": False}],
              instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL_MIN, reference=OPTIMIZING)
        check("maximization", OPTIMAL_MAX, reference=MAXIMIZING)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=3)
        check("compilation_error", UNCOMPILABLE, expected={"compilation_error"}, detail="compilation")
        check("out_of_memory", HOG, expected={"execution_error"}, detail="OutOfMemoryError")

        # Bug-class checks (readiness level 2).
        result = evaluate(candidate("optimization_timeout.java", UNPROVABLE), "readiness", SOLVER,
                          reference_source=EASY_MIN, execution_timeout=3)
        results["optimization_timeout"] = (result["reason"] == "execution_timeout"
                                           and all(item.get("solutions_received", 0) == 0
                                                   for item in result["instances"]))
        check("minimization_step_one", STEP, reference=STEP_REF)
        result = check("optimum_enumeration", SUM, reference=SUM_REF, solution_limit=3)
        results["optimum_enumeration"] = result["accepted"] and result["solutions_checked"] == 3
        check("output_shapes", SHAPES, reference=SHAPES_REF)
        check("instance_shapes", SHAPED, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        result = evaluate(candidate("error_detail.java", FAILING), "readiness", SOLVER, reference_source=REFERENCE)
        results["error_detail"] = (result["reason"] == "execution_error"
                                   and "setValue" in json.dumps(result))
        check("stray_stdout", CHATTY)
        result = check("auxiliary_free_distinct", AUXILIARY, solution_limit=3)
        results["auxiliary_free_distinct"] = result["accepted"] and result["solutions_checked"] == 3
        check("large_model", LARGE, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)

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
