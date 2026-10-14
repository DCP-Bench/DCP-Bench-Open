With a single PBEnc equality of coefficients in the hundreds and a bound in the thousands
(here 297 order literals, bound 2965; in attempt-001 the reference's own coefficients with
bound 94500), the process was killed from outside ("Process exceeded 190 seconds") rather
than ending with the runner's own timeout. Inferred, not measured: the time went into
building the encoding, where SIGALRM cannot interrupt. Attempt-003 replaced the equation with a table of clauses over (apples, mangoes) value pairs and solved in 1.5 s.
