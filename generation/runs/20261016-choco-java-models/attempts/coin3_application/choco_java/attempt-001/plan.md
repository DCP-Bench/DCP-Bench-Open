Find the minimum number of coins that allows one to pay exactly any amount smaller than a given maximum amount using a given set of denominations.
  -> x[i] = number of coins of denomination d[i], domain 0..(M-1)/d[i] (an amount below M never needs more coins of one type)
Print the number of each type of coin used (x) as a list of integers.
  -> declared output "x" = IntVar[n]
pay exactly any amount smaller than the maximum amount (each amount a = 1..M-1)
  -> for each a: y[a][i] = number of coins i used to pay a, domain 0..a/d[i]; m.scalar(y[a], d, "=", a)
  -> y[a][i] <= x[i] (a coin used in a payment must be one of the coins owned)
the minimum number of coins
  -> objective MINIMIZE total, total = m.sum(x)
