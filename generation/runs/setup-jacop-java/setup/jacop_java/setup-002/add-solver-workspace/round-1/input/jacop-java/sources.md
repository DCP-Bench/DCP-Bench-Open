# Sources for `jacop-java`

Tested with JaCoP 4.10.0 (Maven Central `org.jacop:jacop`), org.json 20250517,
Eclipse Temurin JDK 21.0.8 on Ubuntu 24.04 (Docker, linux/amd64).

Existing skills: none found. `npx skills find jacop` returned only unrelated
skills from a user named "jacopen"; a GitHub code search for `SKILL.md` files
mentioning JaCoP found nothing.

- https://github.com/radsz/jacop — README (scope, Maven availability), LICENSE.md (AGPL-3.0), CHANGELOG (4.10 features)
- https://javadoc.io/doc/org.jacop/jacop/4.10.0/index.html — class and constructor names in the Modelling and Solving tables
- https://github.com/radsz/jacop/blob/develop/doc/jacopguide/guideJaCoP.pdf — store, impose, search and solution-listener model
- https://github.com/radsz/jacop/tree/develop/src/main/java/org/jacop/examples/fd — example layout (`ExampleFD`, `SendMoreMoney`, `Queens`)
- https://github.com/stleary/JSON-java — org.json `JSONObject` / `JSONArray` accessors
- https://repo1.maven.org/maven2/org/jacop/jacop/4.10.0/ — jar and POM (dependencies used only by Scala/FlatZinc parts)

Verified by running (JDK 21, JaCoP 4.10.0):

- Search prints `Labeling has finished ...` and `DFS1: ...` on stdout unless `setPrintInfo(false)`.
- `Element` and `Circuit` are 1-based; `Element.choose(i, a, v, -1)` is 0-based; `new ElementInteger(i, int[], v)` is not public and `new Element(..., offset)` is deprecated.
- `searchAll` with an unconstrained auxiliary labelled reports 6 solutions for 3 distinct output tuples.
- Optimisation: `labeling(store, select, cost)` minimises; maximising through `XmulCeqZ(obj, -1, neg)` returns the maximum; `timeOutOccured` is set when the limit stops the search (40-pigeon instance, 1.5 s).
- After `labeling`, the solution stays assigned in the store at its base level; a constraint imposed after a search and only propagated inside the next one is not kept (objective fixing failed until propagated at the base level), hence "fresh `Store` per search".
- `LinearInt` over empty arrays throws `ArrayIndexOutOfBoundsException`; zero weights and repeated variables are fine.
- `IntVar.value()` on an unfixed variable returns a domain bound without error.
- A 20,000-variable depth-first search runs without stack overflow at the default stack size.
- The Quick start and every program in `assets/` (with `scripts/check_assets.py`).
