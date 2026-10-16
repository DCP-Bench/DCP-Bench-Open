# maxicp_java: how this runner realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how MaxiCP in Java expresses it.
Runner: [run.py](run.py), which compiles the submission with `javac` and runs the driver
[java/dcp/Main.java](java/dcp/Main.java), which owns the search, the optimum proof, the enumeration and the
protocol. The helpers are [java/dcp/Model.java](java/dcp/Model.java) (the solver a submission builds into),
[java/dcp/Outputs.java](java/dcp/Outputs.java) and [java/dcp/Instance.java](java/dcp/Instance.java). The solver
skill ([skills/maxicp-java/SKILL.md](skills/maxicp-java/SKILL.md)) covers the MaxiCP API with standalone
programs that have their own `main` and search; this file describes the submission form only.

## Submission file

One Java file, `model.java`, staged as `Submission.java` (javac needs a public class in a file of its name).
It declares **`public class Submission`**, has no `main`, and imports what it uses: `org.maxicp.*` (the raw API:
`CPFactory`, `CPIntVar`, `CPBoolVar`, `CPIntervalVar`, the constraint factories), `dcp.Instance`, `dcp.Model`,
`dcp.Outputs`, and `com.google.gson.*` for raw JSON via `inst.raw`. The class path holds MaxiCP 0.0.3, Gson 2.11.0
and the driver, nothing else. A submission posts constraints; it does not create a search, read or write files,
or print to the protocol.

## Entrypoint

```java
public static void build(Instance inst, Model m, Outputs out)
```

The driver calls it once, by reflection, with a fresh `Model`. Anything thrown from it is an `execution_error`
with the message and the top of the stack, except an `InconsistencyException`, which means a constraint is
refuted at the root: the instance is then `unsat`.

## Instance

`inst` wraps the instance JSON; values reach the model unchanged, arrays 0-based as in the JSON:

- scalars: `getInt`, `getLong`, `getBool`, `getDouble`, `getString`;
- lists: `getIntArray`, `getLongArray`, `getBoolArray`, `getStringArray`;
- nested: `getIntMatrix` (rows may be ragged), `getInt3`;
- `has(key)`, and `raw(key)` for any other shape as a Gson `JsonElement`.

JSON Booleans read as 0/1 where an int is asked for. `getInt` refuses values outside the `int` range (use
`getLong`). Extra keys such as `name` and `note` are present and can be ignored.

## Outputs

`out.put("name", value)` once for each declared name, and no others. A value is a `CPIntVar` (a `CPBoolVar`
is written as 0 or 1), an `int`, `long` or `boolean` constant, or any nesting of Java arrays and `List`s of these
(`CPIntVar[]`, `CPIntVar[][][]`, `CPBoolVar[][]`, `List.of(...)`). A view (`sum`, `mul`, `max`, `element`) is an
output too. A number beyond the `int` range goes through `out.putDigits("name", CPIntVar[] digits, 10)`, most
significant digit first. A repeated name throws. Every output is fixed by the search, so every output is a
value of the solution.

## Objective

`m.minimize(x)` or `m.maximize(x)`, at most once, with `x` a `CPIntVar` (a view such as `sum(...)` or `max(...)`
is fine). Absent: satisfaction. Do not bound it with a value known from elsewhere.

## Solving

- **Branching:** the driver searches with `firstFailBinary` over every variable made with `m.intVar`,
  `m.intVarArray`, `m.boolVar`, `m.boolVarArray`, over every output, and over the objective. A solution fixes all
  of them, so every posted constraint has been checked. One thread.
- **Optimisation:** `optimize` with the bound tightened at each improving solution. The last solution is the
  optimum only when the search is `completed`; a search stopped by the deadline is `timeout` and nothing is
  emitted ("Candidate optimum was not proven"). A completed search with no solution is `unsat`. Otherwise the
  driver posts `objective == optimum` at the root and enumerates optima (below).
- **Enumeration:** each solution is followed by a no-good on the declared output variables (constants excluded),
  so solutions are distinct on the outputs, and the search starts again from the root. Under the limit, the
  end of the search gives `complete` (or `unsat` with no solution at all). With no output variable, one
  solution is reported and the status is `complete`.
- **Time:** the budget counts from JVM start, and the driver stops 0.5 s early (never less than 0.1 s of search),
  so the status is its own. A deadline stop is `timeout`. `run.py` kills a JVM that outlives the budget by 15 s.
- **Protocol:** solutions are written after the search ends, in one batch, followed by one status.

## Compilation

`javac -encoding UTF-8 -nowarn` (heap 512 MB) against the class path above, within the compilation timeout.
Any javac error is `compilation_error`; the messages are on stderr.

## Environment

Image `dcp-eval/maxicp_java:v1`: `eclipse-temurin:21-jdk-noble` (digest pinned in the Dockerfile) plus Python
3.12 for the runner. Jars at `/opt/java/maxicp.jar` (MaxiCP 0.0.3 from Maven Central, sha256 `904df52a…90d6`,
MIT), `/opt/java/gson.jar` (Gson 2.11.0, sha256 `57928d6e…78b`) and `/opt/java/dcp.jar` (the driver). The JVM
runs with the serial collector, one processor, `-Xmx1400m -Xss256m`; an exhausted heap is an `execution_error`
with `OutOfMemoryError` in the detail. Inside the container: no network, a read-only filesystem except `/tmp`,
unprivileged, under the container's memory limit. No licence key or edition limits.

## Traps

- **Variables made with `CPFactory` directly are not branched on** (only outputs and the objective are). Use
  `m.intVar` and the other `Model` methods for every decision variable. Interval variables are not registered:
  make a task's `start` (and `end`, if it matters) an output.
- **Interval variables** made with `makeIntervalVar(cp, len)` are optional; use `makeIntervalVar(cp, false, len)`
  for a task that must run, or `noOverlap` and `makespan` ignore it.
- **`firstFailNary` and `heuristicNary` in MaxiCP 0.0.3** are wrong (one returns an unfixed "solution", the other
  misses the largest value). The driver uses `firstFailBinary` and never calls them, so they do not affect this
  runner.
- **Printing** is harmless: the driver points `System.out` at stderr and writes the protocol itself.
- **An exception in `build`**, such as `InvalidParameterException` from an empty domain, is `execution_error`
  with the Java message in `detail`.
- **Empty domains** (`makeIntVar(cp, 3, 1)`) and bounds at `Integer.MIN_VALUE` or `Integer.MAX_VALUE` are refused.

## Example

The pilot fixture [tests/fixtures/model_maxicp_java.java](../../tests/fixtures/model_maxicp_java.java)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```java
import org.maxicp.cp.CPFactory;
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
    if (inst.getBool("optimize")) {
      m.cp().post(ge(sum(x, y), n));
      m.minimize(sum(x, y));
    } else {
      m.cp().post(eq(sum(x, y), n));
    }
    out.put("x", x);
    out.put("y", y);
  }
}
```
