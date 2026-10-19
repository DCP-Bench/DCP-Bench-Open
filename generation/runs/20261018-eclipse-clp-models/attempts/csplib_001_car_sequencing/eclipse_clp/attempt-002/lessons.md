# Lessons: csplib_001_car_sequencing, eclipse_clp

Not evaluated. Both attempts were checked with `evaluation.check` only.

- The example instance passes quickly with both formulations.
- json:1 (24 car types, 200 cars, 5 options) times out at 120 s and 180 s for every variant tried:
  - attempt-001: element-based option lookup, `first_fail` labelling on the sequence.
  - attempt-002: one-hot 0/1 matrix tied to the sequence by reification, `first_fail` labelling.
  - attempt-002 with `input_order`/`indomain_min`, `input_order`/`indomain_max`, `smallest`/`indomain_min` on the sequence: all time out.
- Likely cause: plain labelling without learning on a tight instance. A value order by remaining demand (Smith's heuristic) was not tried; it needs the demand available inside `search_goal/1`.
