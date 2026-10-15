1 If someone wears a green tie he has to wear a green shirt. -> If(t, r) (plain implication over Bools).
2 A guest may only wear green socks and a green shirt if he wears a green tie or a green hat. -> If(s & r, t | h).
3 A guest wearing a green shirt or a green hat or who does not wear green socks must wear a green tie. -> If(r | h | ~s, t).
4 A guest who is not dressed according to rules 1-3 must pay a $11 entrance fee. -> Iff(n, ~(rule1 & rule2 & rule3)) (n is exactly the non-compliance Bool).
Objective: cheapest choice = 10*t (tie) + 2*h (hat) + 12*s (socks) + 11*n (fee); the shirt is already owned, so r costs 0. -> minimise 10*t + 2*h + 12*s + 11*n.
