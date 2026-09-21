# cutting_stock

The pre-retention check refuses a model that never reads a declared instance
field, because that is the shape of a hardcoded model. Waived here after
checking the reference: `roll_width` appears in its data block and in no
constraint, and `widths` is used only as `len(widths)`. The patterns in
`num_rolls_width` already encode what fits on a roll, so the roll width is not
needed to state the problem the reference states.

The same waiver was applied to this problem for the pumpkin_rust integration,
for the same reason.
