# Addition cryptarithm

Assign a digit 0-9 to each letter so that the addition holds when every word is
read as a decimal number. Different letters get different digits, and no word
of more than one letter starts with 0.

Instance: `{"addends": ["SEND", "MORE"], "sum": "MONEY"}` means
SEND + MORE = MONEY. There may be any number of addends.

Print one solution as `{"digits": {"S": 9, "E": 5, ...}}`, with exactly one
entry per letter that appears. If no assignment exists, print
`{"status": "unsatisfiable"}`.
