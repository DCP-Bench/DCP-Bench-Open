Cards numbered 1 to n are arranged in a circle -> x[p] one-hot Bool xv[p][v] for card v at position p, exactly one card per position, exactly one position per card (permutation)
A frog jumps on card 1 first -> card 1 sits at position 0 (rotation fixed): xv[0][1]
from card k, he jumps directly to the card k places clockwise -> from position p with card v the next position is (p+v) mod n; implication If(y[i][p] & xv[p][v], y[i+1][(p+v)%n]) per step i
frog continues jumping forever / find an arrangement that allows the frog to jump on every card -> step chain y[i][p] (frog on position p at step i), exactly one position per step, every position visited exactly once over steps 0..n-1
Print the card arrangement (x) as n different integers 1..n -> output x[p] = sum v*xv[p][v]
Objective: none (satisfaction)
