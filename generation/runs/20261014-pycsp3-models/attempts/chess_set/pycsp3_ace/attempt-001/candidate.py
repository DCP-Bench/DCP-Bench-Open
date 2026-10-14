from pycsp3 import *

# A joinery makes small and large boxwood chess sets each week.
# We decide how many of each to make so as to maximise profit.

# small_set is the number of small sets made per week
small_set = Var(dom=range(0, 201))
# large_set is the number of large sets made per week
large_set = Var(dom=range(0, 201))
# max_profit is the weekly profit in dollars
max_profit = Var(dom=range(0, 4001))

satisfy(
    # the small set needs 3 lathe hours and the large set 2; four lathes work 40 hours each, 160 hours a week
    3 * small_set + 2 * large_set <= 4 * 40,
    # the small set needs 1 kg of boxwood and the large set 3 kg; only 200 kg a week can be obtained
    small_set + 3 * large_set <= 200,
    # profit is $5 per small set and $20 per large set
    max_profit == 5 * small_set + 20 * large_set,
)

# maximise the weekly profit
maximize(max_profit)
