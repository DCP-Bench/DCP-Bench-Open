Five bananas cost three dollars -> banana price 189 units (1 unit = 1/315 dollar)
seven oranges cost five dollars -> orange price 225 units
nine mangoes cost seven dollars -> mango price 245 units
three apples cost nine dollars -> apple price 945 units
purchase 100 fruits -> bananas = 100 - oranges - mangoes - apples
in 100 dollars -> 189 b + 225 o + 245 m + 945 a == 31500, solved with b substituted into 9 k + 2 m + 27 a == 450 (o = 7 k)
all types of fruits need to be purchased -> k, m, a, b >= 1 when building the table of allowed combinations
exactly one allowed (oranges, mangoes, bananas, apples) combination -> sum of one Bool per combination == 1
bananas and apples should be of minimum quantity -> objective minimize bananas + apples
