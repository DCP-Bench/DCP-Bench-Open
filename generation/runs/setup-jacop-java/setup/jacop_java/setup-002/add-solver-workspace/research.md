# JaCoP research

| Topic | Answer | Source |
|---|---|---|
| Identity | `org.jacop:jacop`, packages `org.jacop.core/constraints/search`. A solver with its own native Java API (also a Scala DSL and a FlatZinc front end). The skill covers the Java API. | README, javadoc |
| Paradigm | CP over finite integer domains (also sets, floats) | README |
| Licence | AGPL-3.0, no key or registration | LICENSE.md |
| Docs | No llms.txt (jacop.eu did not respond). Javadoc on javadoc.io; user's guide PDF in `doc/jacopguide`; examples in `src/main/java/org/jacop/examples/fd` | URLs in sources.md |
| Install | Maven Central jar, 4.10.0 latest release (4.11 only in the changelog of develop). Class files are Java 8 (major 52). Runtime deps in the POM (Scala, slf4j) are not needed by the Java API | verified: probes/Probe.java |
| Verify | `java -cp jacop.jar Probe.java` | verified: probes/probe1.txt |
| Data input | No JSON reader; org.json used. Extra keys are ignored when read by name | verified: Quick start with `qs.json` (has `name`) |
| Variables | `IntVar(store, name, min, max)`, `BooleanVar`; domains above `IntDomain.MaxInt` (536870909) are accepted without error at creation | verified: probes/probe3.txt |
| Constraints | `X..`, `LinearInt`, `SumInt`, `Alldifferent`, `Alldistinct`, `Element.choose`, `table.Table`, `cumulative.Cumulative(Unary)`, `Diff2`, `Circuit`, `Count`, `GCC`, `Max`, `Min` | verified: javap listing, probes 2-4 |
| Logic | `Reified(PrimitiveConstraint, IntVar)`, `Implies`, `IfThen`, `Or`, `And`, `Not`; take only `PrimitiveConstraint` | verified: probes/probe3.txt |
| Solve | `DepthFirstSearch.labeling(store, select[, cost])` returns boolean; `timeOutOccured` field; solution left assigned | verified: probes/probe1.txt |
| Errors | Exceptions for bad arguments; an inconsistent model is just `false`; search chatter on stdout unless `setPrintInfo(false)` | verified: probes/probe2.txt |
| Objectives | Minimise only; maximise via negated cost. Optimal iff `true` and `!timeOutOccured` | verified: probes/probe1.txt, probe2.txt |
| All solutions | `getSolutionListener().searchAll(true)`; duplicates when auxiliaries are labelled (6 vs 3) | verified: probes/probe2.txt |
| Parameters | `setTimeOut(seconds)`, `setTimeOutMilliseconds(ms)`; single-threaded and deterministic | verified: probes/probe1.txt |
| Gotchas | 1-based `Element` and `Circuit`; `new ElementInteger(i,int[],v)` not public, `new Element(...,offset)` deprecated; empty `LinearInt` throws; `value()` on an unfixed variable returns a bound silently; reusing a `Store` after a search keeps the solution assigned and can drop constraints imposed later unless propagated at the base level | verified: probes 1-4, relevel.txt |
| Existing skill | none found (see report) | |
