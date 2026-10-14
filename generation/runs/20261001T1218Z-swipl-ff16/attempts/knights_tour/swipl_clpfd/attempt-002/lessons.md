# Lessons (swipl_clpfd)

1. A Hamiltonian path (open tour) can be stated with circuit/1 by adding one
   extra node that leads to any first square and is entered from the last
   square. Positions along the path then follow from
   `(Next #\= Extra) #==> (NextNumber #= Number + 1)` with element/3.
2. The value order of labeling/2 is only up or down. Variables that range over
   an index into a list of candidates, sorted by a static heuristic (here the
   number of knight's moves of the target square, fewest first), give the
   search that heuristic through `up`. Without it the 10x10 board timed out
   (attempt-001); with it all five boards finish (26 s for 10x10). The same
   device made mario's loose-fuel instance finish.
3. A single-output problem forces the driver to exhaust the search, so any
   multiplicity of auxiliary solutions (handshaking, jobshop) has to be
   removed in the model.
