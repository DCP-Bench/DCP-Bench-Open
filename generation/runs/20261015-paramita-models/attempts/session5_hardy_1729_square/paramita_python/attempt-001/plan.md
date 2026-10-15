Find a combination of 4 different numbers between 1 and 100 -> one-hot Bool per number, exactly one value each (a, b, c, d)
such that the sum of the squares of the two first numbers -> binary bits of a*a and b*a per value, If(one-hot value, bits == v*v)
is equal to the sum of the squares of the other two numbers -> PB equality over the 14 square bits: a^2 + b^2 == c^2 + d^2
four different numbers -> at most one of the four one-hot Bools per value (all pairwise different)
Print the numbers (a, b, c, d) -> outputs a, b, c, d as integer expressions sum(v * onehot)
objective -> satisfaction (no objective)
