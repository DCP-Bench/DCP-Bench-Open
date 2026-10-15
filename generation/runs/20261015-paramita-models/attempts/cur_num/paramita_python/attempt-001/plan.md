The number 48 has this peculiarity, that if you add 1 to it the result is a square number ->
  peculiar + 1 = a*a, a one-hot over 1..100 (exactly one a), sum(a*a * root_a[a]) == peculiar + 1
and if you add 1 to its half, you also get a square number ->
  peculiar even (bit 0 is 0), half = sum(2^k * bit_{k+1}), half + 1 = b*b, b one-hot over 1..70
Print another number with this peculiarity ->
  peculiar in 1..10000 (binary, 14 bits, PB bound), peculiar != 48 (peculiar <= 47 or peculiar >= 49)
Objective -> satisfaction; output peculiar = sum(2^k * bit_k) (integer expression)
