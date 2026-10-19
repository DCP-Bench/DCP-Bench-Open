# All n-queens solutions

Place `n` queens on an `n` by `n` chessboard so that no two queens attack each
other: no two share a row, a column or a diagonal. Find **every** placement,
not just one.

Instance: `{"n": 6}`.

Print each solution on its own line as `{"queens": [c_0, ..., c_{n-1}]}`,
where `c_i` is the 0-based column of the queen in row `i`. Print every distinct
solution exactly once, and nothing else that starts with `{`.
