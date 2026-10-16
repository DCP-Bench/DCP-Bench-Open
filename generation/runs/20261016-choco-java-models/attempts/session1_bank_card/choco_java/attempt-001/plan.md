My bank card has a 4 digit pin, abcd.
  -> a, b, c, d IntVars, each 0..9
no two digits are the same
  -> m.allDifferent(a, b, c, d, "AC")
the 2-digit number cd is 3 times the 2-digit number ab
  -> ab = 10a+b, cd = 10c+d as IntVars; scalar(cd, ab) with cd - 3*ab = 0
the 2-digit number da is 2 times the 2-digit number bc
  -> da = 10d+a, bc = 10b+c as IntVars; scalar(da, bc) with da - 2*bc = 0
Print the PIN (a, b, c, d).
  -> declared outputs a,b,c,d; satisfaction, no objective
