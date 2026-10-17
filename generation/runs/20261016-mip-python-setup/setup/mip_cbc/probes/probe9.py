import mip
m = mip.Model(solver_name="CBC")
x = m.add_var("x", lb=0, ub=3, var_type=mip.INTEGER)
y = m.add_var("y", lb=1, ub=3, var_type=mip.INTEGER)
for label, f in [("x/y", lambda: x / y), ("x**2", lambda: x ** 2), ("x/2", lambda: x / 2)]:
    try:
        print(label, "->", type(f()).__name__)
    except Exception as e:
        print(label, "raises", type(e).__name__, e)
