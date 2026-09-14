Attempt 001 was accepted but Gecode hit the 180 s execution timeout on the
second instance (16 x 16 deck, 10 containers). Attempt 002 added implied `diffn`
and `cumulative` constraints and failed with `execution_error`:
"cumulative: durations and resource usages must be non-negative". The side
lengths were introduced as `var int` expressions, so Gecode saw no non-negative
bound on them even though each equals a container side.

Attempt 003 is attempt 002 with the side lengths declared as variables whose
domain is the two possible sides of that container, which is where the bound
belongs. Lesson for the modelling skill: Gecode's `cumulative` needs durations
and usages whose *declared domains* are non-negative, not merely expressions
that cannot be negative.
