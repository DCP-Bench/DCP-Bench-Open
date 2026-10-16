"""Assign each shift one available worker, at most max_shifts per worker, at minimum
cost. Usage: python model.py [data.json]"""
import json
import sys

from pycsp3 import *

path = sys.argv[1] if len(sys.argv) > 1 else "data.json"
with open(path) as f:
    d = json.load(f)                     # extra keys such as "name" and "note" are ignored

n_shifts = d["shifts"]
available = d["available"]               # ragged: one list per worker
cost = d["cost"]
n_workers = len(available)

# who[s] is the worker on shift s
who = VarArray(size=n_shifts, dom=range(n_workers))
# the workers available for each shift, built from the ragged lists
can_take = [[w for w in range(n_workers) if s in available[w]] for s in range(n_shifts)]

satisfy(
    # a shift goes to a worker who is available for it
    [who[s] in set(can_take[s]) for s in range(n_shifts)],
    # no worker takes more than max_shifts shifts
    [Count(who, value=w) <= d["max_shifts"] for w in range(n_workers)],
)
# cost is a Python list, so cost[who[s]] fails: link worker and cost with a Table of pairs
pay = VarArray(size=n_shifts, dom=set(cost))
satisfy(
    # pay[s] is the cost of the worker on shift s
    Table(scope=(who[s], pay[s]), supports=list(enumerate(cost))) for s in range(n_shifts)
)
minimize(Sum(pay))

status = solve()
if status is OPTIMUM:
    print("Objective:", bound())
    print("Workers:", values(who))
elif status is UNSAT:
    print("Infeasible")
else:
    print("Status:", status)
