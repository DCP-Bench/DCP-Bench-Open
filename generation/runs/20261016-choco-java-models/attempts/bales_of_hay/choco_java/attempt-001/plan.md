bales_of_hay plan
n bales of hay, each with a weight -> bales: IntVar[n] in 0..max weight, sorted nondecreasing (the reference reads bales sorted)
weighed in all possible combinations of two -> one sum variable per pair (i<j): pairSum = bales[i] + bales[j]
weights of the combinations written down in numerical order, without matching -> sort(pairSums, sorted), sorted[k] = weights[k] for each k
objective: none (satisfaction)
