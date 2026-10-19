# Vertex cover (minimise)

**Problem:** smallest set of vertices touching every edge of a 6-vertex graph given as an edge list.
**Shows:** a 2-D parameter matrix (`m` x 2 edge list), indexing a decision matrix by parameter values, a disjunction under `forAll`, `sum` over a 1-D Boolean matrix, an objective variable so the value appears in the output, `minimising`.
**Run:** `savilerow cover.eprime graph.param -run-solver -solutions-to-stdout`
**Expected:** `letting size be 3`
