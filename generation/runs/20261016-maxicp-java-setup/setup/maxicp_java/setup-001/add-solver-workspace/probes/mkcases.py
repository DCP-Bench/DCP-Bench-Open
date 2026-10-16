"""Writes runner test cases: one folder per case with model.java and request.json (probe scaffolding only)."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent / "cases"
HEAD = """import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
"""
TAIL = "  }\n}\n"


def java(body):
    return HEAD + body + TAIL


QUEENS = java("""    int n = inst.getInt("n");
    CPIntVar[] q = m.intVarArray(n, 0, n - 1);
    CPIntVar[] qL = CPFactory.makeIntVarArray(n, i -> minus(q[i], i));
    CPIntVar[] qR = CPFactory.makeIntVarArray(n, i -> plus(q[i], i));
    m.cp().post(allDifferent(q));
    m.cp().post(allDifferent(qL));
    m.cp().post(allDifferent(qR));
    out.put("q", q);
""")

CASES = {
    "sat_queens": (dict(n=8), 3, 10, QUEENS),
    "enum_queens_all": (dict(n=6), 100, 10, QUEENS),
    "opt_max": (dict(n=3), 5, 10, java("""    int n = inst.getInt("n");
    CPIntVar x = m.intVar(0, 2 * n);
    CPIntVar y = m.intVar(0, 2 * n);
    m.cp().post(le(sum(x, y), 2 * n));
    m.maximize(sum(x, y));
    out.put("x", x);
    out.put("y", y);
""")),
    "opt_all_ties": (dict(n=2), 10, 10, java("""    int n = inst.getInt("n");
    CPIntVar[] v = m.intVarArray(4, 0, 2);
    CPIntVar total = sum(v);
    m.cp().post(ge(total, n));
    m.minimize(total);
    out.put("x", v);
""")),
    "unsat": (dict(n=2), 3, 10, java("""    CPIntVar x = m.intVar(0, 1);
    m.cp().post(eq(x, 0));
    m.cp().post(eq(x, 1));
    out.put("x", x);
""")),
    "aux_free": (dict(n=2), 3, 10, java("""    int n = inst.getInt("n");
    CPIntVar x = m.intVar(0, n);
    CPIntVar y = m.intVar(0, n);
    CPIntVar spare = m.intVar(0, 5);
    m.cp().post(eq(sum(x, y), n));
    out.put("x", x);
    out.put("y", y);
""")),
    "error_domain": (dict(n=2), 1, 10, java("""    out.put("x", CPFactory.makeIntVar(m.cp(), 3, 1));
""")),
    "compile_error": (dict(n=2), 1, 10, "this is not java\n"),
    "pigeon_timeout": (dict(n=2), 1, 3, java("""    CPIntVar[] p = m.intVarArray(20, 0, 18);
    for (int i = 0; i < 20; i++) for (int j = i + 1; j < 20; j++) m.cp().post(neq(p[i], p[j]));
    out.put("p", p);
""")),
    "golomb_opt_timeout": (dict(n=2), 1, 3, java("""    int n = inst.getInt("n");
    CPIntVar x = m.intVar(0, 10);
    m.cp().post(ge(x, n));
    CPIntVar[] marks = m.intVarArray(11, 0, 200);
    m.cp().post(eq(marks[0], 0));
    for (int i = 0; i < 10; i++) m.cp().post(lt(marks[i], marks[i + 1]));
    CPIntVar[] diffs = new CPIntVar[55];
    int k = 0;
    for (int i = 0; i < 11; i++) for (int j = i + 1; j < 11; j++) {
      CPIntVar d = m.intVar(0, 200);
      m.cp().post(sum(new CPIntVar[]{marks[j], minus(marks[i])}, d));
      diffs[k++] = d;
    }
    m.cp().post(allDifferent(diffs));
    m.minimize(sum(mul(x, 1000), marks[10]));
    out.put("x", x);
""")),
    "nested_outputs": (dict(n=2), 3, 10, java("""    int n = inst.getInt("n");
    CPIntVar x = m.intVar(0, n);
    CPIntVar y = m.intVar(0, n);
    m.cp().post(eq(sum(x, y), n));
    out.put("cube", new CPIntVar[][][]{{{x, y}, {y, x}}});
    out.put("flags", java.util.List.of(new CPIntVar[]{x, y}));
    CPIntVar[] digits = new CPIntVar[11];
    digits[0] = CPFactory.makeIntVar(m.cp(), 3, 3);
    for (int i = 1; i < 9; i++) digits[i] = CPFactory.makeIntVar(m.cp(), 0, 0);
    digits[9] = x;
    digits[10] = y;
    out.putDigits("big", digits, 10);
    out.put("k", 5);
""")),
    "step_one": (dict(n=2), 1, 10, java("""    int n = inst.getInt("n");
    CPIntVar x = m.intVar(0, 10);
    m.cp().post(le(x, n - 1));
    m.minimize(plus(minus(x), 10));
    out.put("x", x);
""")),
    "large": (dict(n=1500), 1, 120, java("""    int n = inst.getInt("n");
    CPIntVar[] b = m.intVarArray(3000, 0, 1);
    CPIntVar count = m.intVar(0, 3000);
    m.cp().post(eq(count, sum(b)));
    m.cp().post(eq(count, n));
    out.put("b", b);
    out.put("count", count);
""")),
    "chatty": (dict(n=2), 1, 10, java("""    int n = inst.getInt("n");
    System.out.println("building for n = " + n);
    CPIntVar x = m.intVar(0, n);
    CPIntVar y = m.intVar(0, n);
    m.cp().post(eq(sum(x, y), n));
    out.put("x", x);
    out.put("y", y);
""")),
    "no_outputs": (dict(n=2), 1, 10, java("""    CPIntVar x = m.intVar(0, 2);
""")),
}

for name, (instance, limit, timeout, source) in CASES.items():
    folder = ROOT / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "model.java").write_text(source)
    (folder / "request.json").write_text(json.dumps({
        "instance": instance, "solution_limit": limit, "execution_timeout": timeout,
        "compilation_timeout": 60, "legacy": False, "outputs": []}))
print("wrote", len(CASES), "cases")
