Five bananas cost three dollars -> banana price 189 units (1 unit = 1/315 dollar), unary quantity (bits ge_k for k = 2..97)
seven oranges cost five dollars -> orange price 225 units, unary quantity
nine mangoes cost seven dollars -> mango price 245 units, unary quantity
three apples cost nine dollars -> apple price 945 units, unary quantity
purchase 100 fruits -> bananas + oranges + mangoes + apples == 100
in 100 dollars -> 189 b + 225 o + 245 m + 945 a == 31500 (exact spend, constant part of the 1 per type moved to the right)
all types of fruits need to be purchased -> quantity at least 1 per type, domain up to 97 (the other three take at least 3)
bananas and apples should be of minimum quantity -> objective minimize bananas + apples
