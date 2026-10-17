"""Probe 8: what the image can and cannot select (run in the mip_cbc image)."""
import os
import mip

print("solver_name env:", os.environ.get("solver_name"), os.environ.get("SOLVER_NAME"))
for name in ["GRB", "HiGHS", "CBC", ""]:
    try:
        m = mip.Model(solver_name=name)
        print(repr(name), "->", m.solver_name, type(m.solver).__name__)
    except Exception as error:
        print(repr(name), "raises", type(error).__name__, str(error)[:120])
try:
    m = mip.Model()
    print("Model() ->", m.solver_name)
except Exception as error:
    print("Model() raises", type(error).__name__, error)
try:
    import numpy
    print("numpy present")
except ImportError as error:
    print("numpy:", error)
try:
    m = mip.Model(solver_name="CBC")
    m.verbose = 0
    m.max_mip_gap = 0.01
    m.threads = 4
    x = m.add_var("x", lb=0, ub=3, var_type=mip.INTEGER)
    m.objective = x
    m.optimize()
    print("threads after set:", m.threads, "gap", m.max_mip_gap)
except Exception as error:
    print("err", error)
