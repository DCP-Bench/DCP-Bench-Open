# session1_guards_and_apples: plan (Choco 6.0.1)

A boy wants to give an apple to a girl ... passes through num_gates gates, each with a guard
  -> apples[i] = apples before gate i, i in 0..num_gates
After he has given the apple to the girl, he has no apples left (so he holds exactly 1 after the last gate)
  -> apples[num_gates] = 1 (the apple he gives the girl)
He bribes each guard with half of his apples, plus one
  -> apples after gate i = apples[i]/2 - 1, i.e. 2*apples[i+1] + 2 = apples[i] (scalar form)
Whole apples only: half of the apples must be a whole number
  -> implied by the equation (apples[i] = 2*(apples[i+1]+1) is even)
Print the apples before each gate plus the number after the last gate
  -> out.put("apples", apples)
objective: none (satisfaction); bound 2^(n+2) covers 3*2^n - 2
