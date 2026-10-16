Problem: the set {1, 3, 8, 120} has the property that the product of any two members is one less than a perfect square; find a fifth number number >= 0 that keeps the property.
Fifth number number in 0..max_val (instance field) -> intVar(0, max_val)
Product of the fifth number with each member is one less than a square: a*number + 1 = s_a * s_a for a in {1, 3, 8, 120} -> scalar view, m.times(s, s, sq), sq = scalar(number) + 1
Square roots bounded by the largest possible product + 1 (from max_val) -> domain of s_a
The fifth number is a new element of the set, so it differs from each member -> number != a
Objective: satisfaction (none)
