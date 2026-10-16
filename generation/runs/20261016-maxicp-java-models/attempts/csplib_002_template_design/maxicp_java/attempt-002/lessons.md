# csplib_002_template_design, maxicp_java: retry lessons

Outcome: not retained. attempt-002 is accepted on `example` and skips `json:2`
(execution_timeout after 180 s, "Candidate optimum was not proven"). Checked 1 of 2
available instances, below the 80% bar.

What changed from attempt-001:
- production[t] capped at max(demand) (valid: lowering an over-large template keeps
  every variation it prints covered, so optimal solutions stay within the cap).
- Added implied bound sum(production) >= ceil(max_v demand_v / n_slots).
- layout written as plus(minus(gap), cap) over a registered gap variable, so the
  driver's x=min branch tries full templates first.

Findings:
- json:2 has total demand 3665 and n_slots 9, so ceil(3665/9) = 408 is the root lower
  bound and it equals the reference optimum. The proof is trivial once a 408 solution
  is found; the failure is that DFS does not reach a 408 solution inside 180 s.
- The bottleneck is finding a near-tight layout, not proving optimality. Bounds-only
  propagation through mul(production, layout) is weak.
- Variants tried with evaluation.check on example + json:2: (a) capped production
  and implied bound, timeout; (b) layout unregistered so production branches first,
  timeout; (c) gap-view layout so full templates branch first, timeout.

Next ideas (not tried): a tighter per-template product encoding (for example one-hot
sheet counts or a table over copies per sheet), or a model where each template's
fill is forced to sum to n_slots when that is implied by the demand.
