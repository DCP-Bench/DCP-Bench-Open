My bank card has a 4 digit pin, abcd -> four digits a, b, c, d, each one-hot over 0..9 with exactly one value per digit: sum(xv[v]) == 1
no two digits are the same -> per value v: sum over the four digits of xv[v] <= 1
the 2-digit number cd is 3 times the 2-digit number ab -> 10*c + d == 3*(10*a + b)
the 2-digit number da is 2 times the 2-digit number bc -> 10*d + a == 2*(10*b + c)
Objective -> none (satisfaction)
