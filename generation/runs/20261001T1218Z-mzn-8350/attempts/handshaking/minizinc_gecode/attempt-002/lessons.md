# Lessons (handshaking, minizinc_gecode)

- The runner enumerates with MiniZinc `all_solutions` and de-duplicates only afterwards on the declared
  outputs, so a model whose declared outputs do not fix its other variables (here hil only, with the degree
  vector and the handshake matrix free) must finish a full enumeration to report that no second distinct
  output exists. For 8 invited couples I estimate 8! * 2^8 = 10,321,920 labelled solutions by counting (not measured); attempt-001
  (no symmetry breaking) reached `execution_timeout` on the 8- and 6-couple instances
  (evaluation.json of attempt-001). Attempt-002 adds symmetry breaking between interchangeable
  invited couples and between the spouses of a couple: it removes only relabelled copies of a situation, hil is
  the same in all of them, and it was accepted on all 5 instances. The frozen skill says never to add
  solution-removing constraints for speed; this one removes none of the declared outputs' values.
- `where` is a reserved word in MiniZinc (syntax error as a variable name); a 0-based literal array needs
  `array1d(0..k, [...])` or its declared index set mismatches.
