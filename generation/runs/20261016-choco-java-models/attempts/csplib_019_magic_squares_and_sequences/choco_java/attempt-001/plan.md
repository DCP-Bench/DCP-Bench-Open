# Plan: magic sequence of length n (csplib_019)

- "a sequence x_0..x_{n-1} of integers between 0 and n-1" -> x = m.intVarArray("x", n, 0, n-1)
- "for all i in 0 to n-1, the number i occurs exactly x_i times in the sequence" -> for each i: m.count(i, x, x[i]) (count of value i equals x_i)
- "print the magic sequence (x)" -> output x
- implied: the counts add up to n (every position holds one value) -> m.sum(x, "=", n)
- objective: satisfaction (none)
