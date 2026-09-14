Attempt 001 was accepted but Gecode hit the 180 s execution timeout on the
second instance (16 x 16 deck, 10 containers): a plain four-way disjunction per
pair propagates very little. Attempt 002 adds two implied constraints that
remove no solution:

- `diffn` over the placed rectangles, which the pairwise disjunction already
  implies whenever every separation is non-negative (guarded on the data, so a
  hypothetical negative separation falls back to the disjunction alone);
- a `cumulative` relaxation along each axis, the standard redundant constraint
  for rectangle packing: sweeping across the deck, the heights of the containers
  cut by the sweep line cannot exceed the deck.
