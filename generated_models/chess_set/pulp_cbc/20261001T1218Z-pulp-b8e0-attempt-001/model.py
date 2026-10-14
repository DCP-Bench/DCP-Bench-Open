"""Chess sets: a joinery makes small and large boxwood chess sets under limits on lathe hours
and boxwood, and chooses how many of each to make per week to maximize profit.

The model reports the number of small and large sets and the maximum profit.
"""
import pulp


def build(instance):
    del instance  # the problem has no instance data; its figures are below

    problem = pulp.LpProblem("chess_set", pulp.LpMaximize)

    # sets made per week; the bounds 0..100 and 0..10000 are the reference's domains
    small_set = pulp.LpVariable("small_set", 0, 100, cat="Integer")
    large_set = pulp.LpVariable("large_set", 0, 100, cat="Integer")
    max_profit = pulp.LpVariable("max_profit", 0, 10000, cat="Integer")

    # boxwood: a small set uses 1 kg and a large set 3 kg, of 200 kg per week
    problem += small_set + 3 * large_set <= 200
    # lathes: a small set takes 3 hours and a large set 2 hours, of 160 lathe-hours
    problem += 3 * small_set + 2 * large_set <= 160
    # profit: $5 per small set and $20 per large set
    problem += max_profit == 5 * small_set + 20 * large_set

    # maximize the profit
    problem += max_profit

    return problem, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}
