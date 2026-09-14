# csplib_012_nonogram

Shade a grid so each row and column matches its sequence of block lengths.

- Instance inputs: `rows`, `cols`, `row_rules`, `col_rules` (and the rule-length
  fields, which only describe the padding). A zero entry in a rule is padding,
  not a block.
- Output: `board` — a rows x cols matrix of 0/1.
- Satisfaction. The reference builds one automaton per line from its rule and
  accepts the line with a Regular constraint; this model builds the same
  automaton, arc for arc, and states it with `automaton/3`.
