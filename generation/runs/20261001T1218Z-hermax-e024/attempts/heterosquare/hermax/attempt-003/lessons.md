Sums of wide integers in hermax (measured)

heterosquare attempt-001 (one weighted equation per line over int variables): n=6 165.9 s, n=7 killed
at the limit with no solution. attempt-002 (m.sum_var per line): n=6 81.6 s, n=7 189.7 s timeout.
attempt-003 (one-hot cell values, binary digits per cell, column adders built from full and half adders
written as clauses, sums compared digit by digit): all five instances 1.4 to 2.0 s.
fixed_charge: attempt-001 (unit-step soft clauses, one weighted equation for z) 37 to 87 s per instance and
the n=288 instance killed at 190 s; attempt-002 (m.scale + m.sum_var) no better; attempt-004 (profit written
in binary digits, z added up by a chain of single weighted literals) 3.6 to 8.4 s on all five.
