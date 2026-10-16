Problem: buy 100 fruits (bananas, oranges, mangoes, apples) for exactly 100 dollars, every type at least once, minimise bananas and apples.
Five bananas cost three dollars -> price per banana 3/5 dollars; scaled by 315 to integers: 189 per banana -> scalar(prices, "=", 31500) with the budget also scaled
seven oranges cost five dollars -> 5/7 dollar each; scaled: 225 per orange
nine mangoes cost seven dollars -> 7/9 dollar each; scaled: 245 per mango
three apples cost nine dollars -> 3 dollars each; scaled: 945 per apple
100 fruits in total -> sum of the four quantities = 100
100 dollars in total -> scalar of the four quantities with the scaled prices = 100*315 = 31500
all types must be purchased -> each quantity >= 1
objective: minimise bananas + apples -> setObjective MINIMIZE on sum(bananas, apples)
