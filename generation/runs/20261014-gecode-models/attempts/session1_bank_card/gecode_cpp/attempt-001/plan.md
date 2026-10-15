PIN abcd is a 4-digit number, digits 0..9 each (the description gives no leading-digit rule, and the constraints decide it)
no two digits are the same -> distinct(*this, p, IPL_DOM)
the 2-digit number cd is 3 times the 2-digit number ab -> linear(*this, {10,1,-30,-3}, {c,d,a,b}, IRT_EQ, 0) [10c+d = 3(10a+b)]
the 2-digit number da is 2 times the 2-digit number bc -> linear(*this, {10,1,-20,-2}, {d,a,b,c}, IRT_EQ, 0) [10d+a = 2(10b+c)]
branching: all four digits, INT_VAR_SIZE_MIN, INT_VAL_MIN (satisfaction, no objective)
outputs: a, b, c, d (the PIN digits in order)
