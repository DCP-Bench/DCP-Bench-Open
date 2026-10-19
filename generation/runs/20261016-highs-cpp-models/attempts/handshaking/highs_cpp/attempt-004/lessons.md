# handshaking, highs_cpp: lessons

Status: not accepted. Every evaluated attempt hit `execution_timeout` on the `example` instance (n = 8, 18 people), so no instance was checked (0 of 5).

- attempt-001 (pairwise `hands[i] != hands[j]` via binary indicators with big-M = 2n+1): timed out before any solution.
- attempt-003 (per-person one-hot answer, answers form a permutation of 0..2n, `hands[p] = answer`): found one solution (hil = 8) in the 180 s budget, then the enumeration's second solve did not finish.
- attempt-004 (as 003, but hil is a single integer column tied to `hands[0]`, so the no-good covers one column): same behaviour, one solution, then timeout.

Reading: the second solve must prove that no other value of hil exists. HiGHS does not finish that proof in the budget with these formulations. Not tried: a stronger formulation of the handshake graph (degree-sequence cuts), which is the next thing to test.
