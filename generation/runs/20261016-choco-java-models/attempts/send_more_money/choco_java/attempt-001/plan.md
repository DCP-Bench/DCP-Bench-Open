Cryptarithmetic: each letter (s, e, n, d, m, o, r, y) is a unique digit from 0 to 9.
  -> s,e,n,d,m,o,r,y in 0..9 (problem-given domain); m.allDifferent(letters, "AC")
the first letter of each word cannot be zero.
  -> s >= 1 and m >= 1 (domains 1..9)
SEND + MORE = MONEY
  -> SEND, MORE, MONEY as IntVars defined by m.scalar over their digits (weights 1000,100,10,1 and 10000,1000,100,10,1)
  -> m.arithm(SEND, "+", MORE, "=", MONEY) posted
Print the values assigned to each letter (s, e, n, d, m, o, r, y).
  -> declared outputs d,e,m,n,o,r,s,y as IntVar each; satisfaction, no objective
