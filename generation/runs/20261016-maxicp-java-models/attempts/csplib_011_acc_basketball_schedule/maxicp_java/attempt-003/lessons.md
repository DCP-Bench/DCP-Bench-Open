# csplib_011_acc_basketball_schedule: lessons from three attempts

All three attempts evaluated to `execution_timeout` on the example instance (180 s, no solution received).
The instance has no other rows, so `no_instance_verified` on every attempt. No solution was ever seen,
so no output convention or constraint has been checked against the evaluator.

- attempt-001: 2592 venue Booleans (`home[d][i][j]`, `bye[d][i]`), with the mirror as equalities on
  playsOn. Timeout.
- attempt-002: decisions are `config[d][i]` in 0..8 and `where[d][i]` in 0..2. Meetings and venues are
  reified views (`isEq`, `mul`). Added redundant per-date counts (one bye, four home matches) and a
  season home count of eight per team. `where` was kept out of the registered variables, so the driver
  branches on the 162 opponent variables first. Timeout.
- attempt-003: attempt-002 plus `allDifferent` over the bye team of each mirror pair. Timeout.

Reasoning behind the redundant constraints: the mirror makes the nine date pairs into nine rounds, each
with exactly one bye team, so the bye teams form a permutation. Per-date counts follow from that.

Open questions, not verified:
- Plain DFS (no learning, no restarts) may simply not reach a first solution in 180 s with these
  encodings. The remaining lever is a decomposition by mirror round (one matching per round) with
  stronger propagation, or a different branching order that fixes the venue pattern per team first.
- The bye convention (`config[d][i] = i` for a bye, 0-based team indices) was chosen by reading the
  description. It is not checked against the reference.
- Constraint indices map statement dates to 0-based indices (weekend = odd index, last date = 17).
  This was checked by hand only.
