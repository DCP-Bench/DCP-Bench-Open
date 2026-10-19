# choco_java: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Choco in Java
expresses it. Runner: [run.py](run.py), which compiles the submission with `javac` and runs
the driver [java/dcp/Main.java](java/dcp/Main.java), which owns solving, enumeration and the
protocol. The data and output helpers are [java/dcp/Instance.java](java/dcp/Instance.java)
and [java/dcp/Outputs.java](java/dcp/Outputs.java). The solver skill
([skills/choco-java/SKILL.md](skills/choco-java/SKILL.md)) covers the Choco API with
standalone programs (own `main`, own `solve()` loop, printing); [Example](#example) below
shows the submission form.

## Submission file

One Java file, `model.java`, staged as `Submission.java` (javac needs a public class in a
file of its name). It declares **`public class Submission`**, has no `main`, and imports
what it uses: `org.chocosolver.solver.Model`, the variable types, `dcp.Instance` and
`dcp.Outputs`. The class path holds Choco 6.0.1 (jar with dependencies), Gson 2.11.0 and
the driver jar, nothing else. Do not name a class of your own `Model`: it hides Choco's.

## Entrypoint

```java
public static void build(Instance inst, Model m, Outputs out)
```

The driver creates the `Model` and hands it over: `build` posts constraints on it, declares
the outputs, and sets the objective. It does not call `solve()`, `limitTime()` or
`reset()`. An optional `public static SettingsBuilder settings()` is passed to `new
Model(...)`; it is the only way to turn on lazy clause generation (LCG). For optimisation,
and on every enumeration step under LCG, the driver calls `build` again on a fresh model,
so it must be deterministic.

## Instance

`inst` wraps the instance JSON (0-based arrays) and names the field in every error:

- scalars: `getInt`, `getLong`, `getBool`, `getDouble`, `getString`;
- lists: `getIntArray`, `getLongArray`, `getBoolArray`, `getStringArray`;
- nested: `getIntMatrix` (rows may be ragged), `getInt3`;
- `has(key)`, and `raw(key)` for any other shape as a Gson `JsonElement`.

JSON Booleans read as 0/1 where an int is asked for. `getInt` refuses a value outside the
`int` range (use `getLong`). The brief's shapes are those of the example instance: take
every size, output lengths included, from the instance itself.

## Outputs

`out.put("name", value)` once for each declared name, and no others (an extra name, such
as an undeclared objective, is `invalid_output`; a repeated name throws). A value is an
`IntVar`, a `BoolVar` (written as 0/1), an `int`/`long`/`boolean` constant, or any nesting
of arrays and `List`s of these (`IntVar[]`, `IntVar[][]`, `BoolVar[][]`, `List.of(r1,
r2)`, `IntVar[][][]`). A derived value is output through an IntVar (`m.sum("total", x)`,
`e.intVar()`). A number beyond the `int` range goes through `out.putDigits("name",
IntVar[] digits, 10)`, most significant digit first. An output not fixed in a solution is
an error; the driver's completed search fixes every variable.

## Objective

`m.setObjective(Model.MINIMIZE or Model.MAXIMIZE, v)` once, on an `IntVar` (anything else
is an `execution_error`: "the objective must be an IntVar"). Do not bound it with a value
known from elsewhere.

## Solving

- **Search:** a strategy set in `build` with `m.getSolver().setSearch(...)` (and restarts)
  is kept; the driver then calls `makeCompleteStrategy(true)` so it covers every variable.
  One thread.
- **Optimisation:** branch and bound (`while (solver.solve())`) until the search ends. The
  last solution is the optimum only when the state is `TERMINATED`; a stop by the deadline
  (`STOPPED`) is `timeout` and nothing is emitted. Then a fresh model with the objective
  cleared and `objective = optimum` posted enumerates further optima.
- **Enumeration:** after each solution the driver resets the solver and posts a no-good on
  the declared output variables, so solutions are distinct on the outputs and the next one
  must also come quickly. Under LCG (Choco 6.0.1 fails on constraints posted after a
  reset) every step solves a fresh model with all no-goods.
- **Time:** the budget counts from JVM start, and the driver stops 0.5 s early so the
  status is its own. `run.py` kills a JVM that outlives the budget by 15 s.

## Compilation

`javac` (Java 21, `-nowarn`, 512 MB heap) against the class path above, within the
compilation timeout. Any javac error is `compilation_error`; the messages are on stderr.

## Environment

Image `dcp-eval/choco_java:v1` (`eclipse-temurin:21-jdk-noble`, plus Python 3.12 for the
runner). Jars at `/opt/java/choco-solver.jar`, `/opt/java/gson.jar`, `/opt/java/dcp.jar`,
checked against Maven Central's hashes; no Ibex, so `realVar` is unavailable. The JVM runs
with the serial collector, one processor and `-Xmx1400m -Xss256m`, leaving room under the
2 GiB container limit so an exhausted heap ends as an `OutOfMemoryError` (`execution_error`
with the message) rather than a kernel kill.

Inside the container: no network, a read-only filesystem except `/tmp`, user 65534, the
submission and `request.json` under `/input`. The entrypoint is the runner; for an ad hoc
run override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/choco_java:v1 -c '...'`.

## Traps

- **Printing is harmless but never output:** the driver points `System.out` at stderr and
  keeps the protocol stream to itself. Values are reported through `out.put` alone.
- **An exception in `build`** (a missing field, a repeated output, a Choco error) is
  `execution_error` with the Java message and the top of the stack trace in `detail`.
- **`allDifferent` over views** (`m.offset`, `m.mul`, `m.neg`) with `"AC"` or the default
  consistency can throw `java.lang.Error: This element is not present in the in-list` in
  6.0.1, an `execution_error`; use `"AC_REGIN"` or `"BC"` (see the skill).
- **A constraint not posted** (`m.allDifferent(x);` without `.post()`) is silently ignored,
  and shows up as `invalid_solution`.
- **LCG** is safe only for the constraints the skill lists as checked; others throw
  (`execution_error`) or, for `m.not(allDifferent)`, give wrong answers (`invalid_solution`).
- **Free auxiliaries** do not cause repeats (the no-good is on the outputs), but every
  solution costs a search from the root.

## Example

The pilot fixture [tests/fixtures/model_choco_java.java](../../tests/fixtures/model_choco_java.java)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```java
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    IntVar x = m.intVar("x", 0, n);
    IntVar y = m.intVar("y", 0, n);
    if (inst.getBool("optimize")) {
      m.arithm(x, "+", y, ">=", n).post();
      IntVar total = m.intVar("total", 0, 2 * n);
      m.sum(new IntVar[]{x, y}, "=", total).post();
      m.setObjective(Model.MINIMIZE, total);
    } else {
      m.arithm(x, "+", y, "=", n).post();
    }
    out.put("x", x);
    out.put("y", y);
  }
}
```

A fuller one (row seating, every constraint block commented with the description's words):

```java
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Row seating: seat n guests in a row of n chairs so that no two enemies sit side
// by side, and minimise the total distance from each guest's preferred chair.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int[] preferred = inst.getIntArray("preferred");
    int[][] enemies = inst.getIntMatrix("enemies");
    IntVar[] seat = m.intVarArray("seat", n, 0, n - 1);   // seat[g]: chair of guest g
    IntVar[] guest = m.intVarArray("guest", n, 0, n - 1);  // guest[c]: guest on chair c

    // every chair holds exactly one guest
    m.inverseChanneling(seat, guest).post();

    // enemies never sit side by side
    for (int[] pair : enemies) m.distance(seat[pair[0]], seat[pair[1]], ">", 1).post();

    // minimise the total distance from the preferred chairs
    IntVar[] away = new IntVar[n];
    for (int g = 0; g < n; g++) away[g] = seat[g].dist(preferred[g]).intVar();
    IntVar total = m.sum("total", away);
    m.setObjective(Model.MINIMIZE, total);

    out.put("seat", seat);
    out.put("total", total);
  }
}
```
