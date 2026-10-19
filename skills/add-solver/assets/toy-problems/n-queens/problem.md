# N-queens

Place `n` queens on an `n` by `n` chessboard so that no two queens attack each
other: no two share a row, a column or a diagonal.

Instance: `{"n": 8}`.

Print one solution as `{"queens": [c_0, ..., c_{n-1}]}`, where `c_i` is the
0-based column of the queen in row `i`. If no placement exists, print
`{"status": "unsatisfiable"}`.
