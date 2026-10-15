Progress City wants the fewest buses so that the buses on duty meet the demand in each 4-hour slot.
  -> x[i] = number of buses starting in slot i (IntVarArray, domain 0..max demand, a bound derived in the model); output "x".
Each bus works 8 successive hours, so a bus starting in slot i covers slots i and i+1.
  -> x[i-1] + x[i] >= demand[i] (cyclic, index (i+n-1)%n), linear(*this, {x[i-1], x[i]}, IRT_GQ, demand[i], IPL_BND).
The schedule is a day that repeats, so slot 5 is followed by slot 0 (the wrap-around).
  -> the cyclic index in the same constraint, no extra post.
The buses needed in total are the number of buses to minimise.
  -> total = expr(*this, sum(x)); minimize(total). Objective direction: minimize.
Branching on the decisions.
  -> branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN()); total is fixed by x.
