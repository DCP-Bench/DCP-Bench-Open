#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/diet1.py

"""
Given the prices and the nutritional requirements (at least) for each nutrition type, what is the optimal diet?
The optimal diet is to minimize the cost of the products:

Type of                        Calories   Chocolate    Sugar    Fat
Food                                      (ounces)     (ounces) (ounces)

Chocolate Cake (1 slice)       400           3            2      2
Chocolate ice cream (1 scoop)  200           2            2      4
Cola (1 bottle)                150           0            4      1
Pineapple cheesecake (1 piece) 500           0            4      5

Print the optimal cost of the diet (cost).
"""

# Data
n = 4
price = [50, 20, 30, 80]  # in cents
limits = [500, 6, 10, 8]  # requirements for each nutrition type
# End of data

# Import libraries
from cpmpy import *
import json


# macros for each food
calories = [400, 200, 150, 500]
chocolate = [3, 2, 0, 0]
sugar = [2, 2, 4, 4]
fat = [2, 4, 1, 5]

x = intvar(0, 10000, shape=n)
cost = intvar(0, 1000, name="cost")
model = Model(
    [
        sum(x * calories) >= limits[0],
        sum(x * chocolate) >= limits[1],
        sum(x * sugar) >= limits[2],
        sum(x * fat) >= limits[3],
        cost == sum(x * price),
    ],
    minimize=cost
)

# Solve and print the solution
model.solve()

# Print the solution
solution = {"cost": cost.value()}
print(json.dumps(solution))
# End of CPMPy script
