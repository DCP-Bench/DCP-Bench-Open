# autoref on eclipse_clp: lessons

Attempt 001 (rejected, invalid_solution). Two faults:

1. The inner `foreach` that builds the booleans `Bj #= (Xj #= I)` did not take `I` as a `param`. ECLiPSe warned "Singleton local variable I in do-loop" and the constraint was free in `I`. Fix: `param(I)` on the inner loop.
2. With the term domain `0..N+2`, the literal reading admits solutions the instances rule out. For n=3, m=0 the enumerator also gave S=(4,0,0,0,0). The instance note says the only solution is (2,1,2,0,0). The same holds for (1,0) giving (2,0,0) and (4,0) giving (5,0,0,0,0,0).

Attempt 002 (accepted, 5/5 instances checked) bounds every term to `0..n`. The description does not state this bound. It is inferred from the instance notes (only (2,1,2,0,0) for n=3, m=0; no solution for (1,0), (4,0), (6,2)). Treat it as a reading the reference enforces, not a constraint the description spells out. The model still constrains each si by the occurrence count, and the output dimension follows the instance's n.

Probe runs used the ad hoc container command with a scratch file outside the repository. No reference file was opened.
