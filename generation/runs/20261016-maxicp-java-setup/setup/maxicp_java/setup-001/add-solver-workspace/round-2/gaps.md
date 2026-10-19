# MaxiCP Java skill: round 2 gaps

Tester: fresh agent, reading only `solvers/maxicp_java/skills/maxicp-java/` (SKILL.md, assets/ examples and READMEs). Final run: 18/18 in `results.txt`.

## 1. Install section does not work in the test container

- **Missing:** the Install section downloads `lib/maxicp-0.0.3.jar` and `lib/gson-2.11.0.jar` with curl and sets `CLASSPATH="$PWD/lib/..."`. The toy runner runs the container with `--network none`, and the image sets no `CLASSPATH`.
- **Hit:** no error. I could not follow the install step as written.
- **Fix used:** `find` in the image showed `/opt/java/maxicp.jar` and `/opt/java/gson.jar`. I ran `java -cp /opt/java/maxicp.jar:/opt/java/gson.jar Model.java ARGS`.
- **Suggested fix:** say where the jars live in the test image, or give the `-cp` form for a container with no network.

## 2. Image entrypoint is not Java

- **Hit:** the image's entrypoint is `python3 /opt/runner/run.py`, so `docker run IMAGE java ...` would run the Python runner. The skill's runner example (`IMAGE python3 /m/{problem}.py`) is Python-only.
- **Fix used:** `docker run --entrypoint java ... IMAGE -cp ... /m/{problem}.java {instance}`.
- **Suggested fix:** add a Java `--cmd` example for `run_toy_tests.py` (the toy README only says "a compiled language builds first"). Note `--entrypoint` for images with a non-default entrypoint.

## 3. Infeasibility at post time: unclear in the Modelling section

- **Error:**
  ```
  Exception in thread "main" inconsistency | at org.maxicp.cp.engine.core.MaxiCP.fixPoint(MaxiCP.java:68) | at org.maxicp.cp.engine.core.MaxiCP.post(MaxiCP.java:104) | at org.maxicp.cp.engine.core.MaxiCP.post(MaxiCP.java:98) | at Cryptarithm.main(cryptarithm.java:53)
  ```
  Instance: `cryptarithm/ab-ab-aaa` (AB + AB = AAA, infeasible). The failing line was the root `cp.post(eq(...))`.
- **Why it was missed:** the Modelling section says only that `cp.post` "throws `InconsistencyException`". The Common issues row ("Catch it where the post is outside a search") has the rule, but I read Modelling first and did not connect it to the infeasible case.
- **Fix used:** wrapped the root post in `try { ... } catch (InconsistencyException refuted) { print {"status": "unsatisfiable"} }`.
- **Suggested fix:** in Modelling, say that a root refutation at `post` is an infeasible model: catch it and report zero solutions. Link the Common issues row from there.

## 4. Missing import for InconsistencyException in the no-good snippet

- **Hit:** the All solutions snippet catches `InconsistencyException` but gives no import. I needed `org.maxicp.util.exception.InconsistencyException`, which I found only in the Optimisation example (`min-makespan/MinMakespan.java`).
- **Fix used:** added `import org.maxicp.util.exception.InconsistencyException;`.
- **Suggested fix:** add the import to the snippet, or say it is in `org.maxicp.util.exception`.

## 5. Java file and class naming with hyphenated problem names

- **Unclear:** the examples use `public class X` in `X.java`. Toy files are named `n-queens.java`, which cannot hold a public class with a hyphen in its name. The skill does not say how a single-file program should be named or how the runner should launch it.
- **Fix used:** Java source-launcher programs (`java File.java`) with non-public classes (`NQueens`, `Knapsack`, ...) in files named after the problem. No error followed, but I had to guess the convention.
- **Suggested fix:** one sentence on the source-launcher form: the class name is free, and the file name only needs to end in `.java`.

## Not a gap, for the record

- No API name was wrong in the skill. Everything used (`plus`, `minus`, `max`, `mul` with a bool var, `neq`, `noOverlap`, `endBeforeStart`, `makespan`, `optimize`, `cp.maximize`, `solve(predicate)`) worked as documented.
- Round-1 `results.txt` holds no command line, so the exact command used there is unknown. I used the SKILL step 2 docker form adapted to Java, with the entrypoint override from gap 2.
