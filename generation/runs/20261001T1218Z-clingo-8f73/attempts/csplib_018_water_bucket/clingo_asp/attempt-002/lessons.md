Grounding lesson for clingo_asp (measured: attempt-001 hit the 2048 MB memory limit within the first minute, attempt-002 with the fix ran in 1.4 s).

When a rule derives a state atom with arithmetic in its head (state(T+1,I,X-Q)), the grounder pairs
atoms without knowing which ones belong to the same state. It then derives out-of-range values
(negative amounts, amounts above the capacity), and the next step builds on those, so the grounding
grows at every step. Bounding the derived value with a domain atom in the rule body
(amount(I,X-Q)) removes this. Symptom: memory_limit with only "info: global variable in tuple of
aggregate element" in the detail.
