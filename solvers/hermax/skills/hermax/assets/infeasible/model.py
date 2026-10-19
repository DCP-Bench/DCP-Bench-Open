# Four tasks must each get a distinct time slot out of three: no schedule exists.
from hermax.model import Model

TASKS = 4
SLOTS = 3

m = Model()
slot = m.int_vector("slot", TASKS, 0, SLOTS - 1)  # slot[t]: the time slot of task t
m &= slot.all_different()

r = m.solve()
print("status:", r.status)
if r.ok:
    print("slots:", [r[s] for s in slot])
else:
    print("no schedule: the solver proved there is none")
