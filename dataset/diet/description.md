Given the prices and the nutritional requirements (at least) for each nutrition type, what is the optimal diet?
The optimal diet is to minimize the cost of the products:

```text
Type of                        Calories   Chocolate    Sugar    Fat
Food                                      (ounces)     (ounces) (ounces)

Chocolate Cake (1 slice)       400           3            2      2
Chocolate ice cream (1 scoop)  200           2            2      4
Cola (1 bottle)                150           0            4      1
Pineapple cheesecake (1 piece) 500           0            4      5
```

`price` holds the price of one unit of each food, in the order of the table, and `limits` holds the minimum required of
each nutrition type: calories, chocolate, sugar and fat. Each food is bought in a whole number of units.

Print the optimal cost of the diet (cost).
