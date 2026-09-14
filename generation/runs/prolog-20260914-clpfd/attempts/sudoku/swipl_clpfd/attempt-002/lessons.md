Attempt 001 was rejected as `invalid_solution`: the grid it returned repeated
values inside a 3 x 3 block. The block constraint was there, but it was applied
to the wrong terms — the block's cells were collected with findall/3, which
copies its template, so `all_distinct/1` constrained fresh copies of the cells
instead of the grid itself.

Attempt 002 collects the cells by mapping over the row and column indices, which
builds the list by unification and keeps the grid's own variables. The general
rule for this integration: findall/3 is safe for ground data such as index
pairs, and never for decision variables.
