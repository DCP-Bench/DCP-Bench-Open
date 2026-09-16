import time
from pychoco.model import Model

# time limit behaviour: a deliberately large enumeration
m3 = Model("h")
n = 12
vs = [m3.intvar(0, 9, name=f"v{i}") for i in range(n)]
s3 = m3.get_solver()
s3.limit_time("2s")
t0 = time.monotonic()
found = 0
while s3.solve():
    found += 1
elapsed = time.monotonic() - t0
print("limited run found", found, "in %.2fs" % elapsed, "-> hit limit:", elapsed >= 1.9)

# optimal with scalar
m4 = Model("o")
a = m4.intvar(0, 100, name="a"); b = m4.intvar(0, 100, name="b")
m4.arithm(a, "+", b, ">=", 40).post()
obj = m4.intvar(0, 200, name="obj")
m4.scalar([a, b], [1, 1], "=", obj).post()
s4 = m4.get_solver()
sol = s4.find_optimal_solution(obj, maximize=False)
print("optimal obj:", sol.get_int_val(obj))
print("solution methods:", sorted(x for x in dir(sol) if not x.startswith("_")))
