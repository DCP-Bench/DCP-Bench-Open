# cutting_stock

The pre-retention check in this run refuses a model that never reads a declared
instance field, because that is the shape of a hardcoded model. This one is
waived after checking the reference: `roll_width` is declared in the data block
and never appears in any constraint. `widths` is used only as `len(widths)`.

The cutting patterns in `num_rolls_width` already say how many pieces of each
width a roll yields, so the roll width is not needed to state the problem the
reference states. Deriving the patterns from `roll_width` and `widths` would be
a different, larger problem.

attempt-001 carried the same constraints; attempt-002 adds the comment saying
why those two fields are absent, so a reader is not left wondering.
