The integers 1,3,8, and 120 form a set with a remarkable property: the product of any two integers is one less than a perfect square ->
  for each a in {1,3,8,120}: a*x + 1 == c*c; c one-hot over 1..isqrt(a*max_val+1) (exactly one); c*c in binary bits s_k, If(root_c, s_k == bit_k of c*c); sum(2^k s_k) == a*x + 1
Find a fifth number (larger than or equal to 0) that can be added to the set without destroying this property ->
  x in 0..max_val (instance max_val), binary bits, PB bound sum(2^k bit_k) <= max_val
Print this number (number) ->
  output number = sum(2^k bit_k) (integer expression)
Objective ->
  satisfaction (no objective)
