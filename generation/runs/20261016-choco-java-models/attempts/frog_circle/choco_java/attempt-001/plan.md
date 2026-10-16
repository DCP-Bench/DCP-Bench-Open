Cards numbered 1 to n are arranged in a circle: position p holds card x[p].
  -> IntVar x[p] in 1..n, allDifferent(x, "AC") (a permutation of the cards)
A frog jumps on card 1, then jumps the card 1 place clockwise; from card k it jumps k places clockwise.
  -> from position p the next position is (p + x[p]) mod n: nxt[p] = element(table_p, x[p], 1-based), table_p[k] = (p + k) mod n
The frog starts on card 1.
  -> card 1 is the first card of the arrangement, position 0: x[0] = 1 (the start convention; a rotation of any solution is also one)
The frog jumps on every card starting from card 1.
  -> the walk pos[0] = 0, pos[i+1] = nxt[pos[i]] has its first n positions all different: allDifferent(pos, "AC")
  (a walk that covers all n cards must do so in its first n steps; it may loop after that, so no circuit)
Print the card arrangement x as n different integers 1..n.
  -> output x
Satisfaction problem: no objective.
