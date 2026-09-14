Attempt 001 timed out before the search even started. The row lambda was written
`{Cells}/[Row]>>(length(Row, N), Row ins 1..Cells)` with `N` left out of the
declared free variables: yall expands a lambda at compile time, so a variable
that is not named in `{...}` is local to the lambda however bound it is at call
time. `length(Row, N)` therefore ran with an unbound length and enumerated rows
of every size forever.

Attempt 002 declares both free variables. The general rule for this integration:
every variable a lambda uses from the surrounding clause must appear in its
`{...}` set.
