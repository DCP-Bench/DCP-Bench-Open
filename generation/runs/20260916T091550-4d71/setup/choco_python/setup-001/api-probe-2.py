from pychoco.model import Model
m = Model("api2")
ok, bad = [], []
def t(name, fn):
    try:
        fn(); ok.append(name)
    except Exception as e:
        bad.append(f"{name}: {type(e).__name__}: {e}")
x = m.intvar(0, 5, name="x"); y = m.intvar(0, 5, name="y"); z = m.intvar(0, 25, name="z")
vs = [m.intvar(0, 5, name=f"v{i}") for i in range(3)]
t("sum(vars,op,target-var)", lambda: m.sum(vs, "=", z).post())
t("sum(vars,op,const)", lambda: m.sum(vs, "=", 5).post())
t("min(res,vars)", lambda: m.min(z, vs).post())
t("max(res,vars)", lambda: m.max(z, vs).post())
t("square", lambda: m.square(z, x).post())
t("pow", lambda: m.pow(x, 2, z).post())
t("cumulative", lambda: None)
print("OK:", ok)
for f in bad: print("FAIL", f)
# help signatures
import inspect
for n in ("sum","min","max","element","count","global_cardinality","among","cumulative","diff_n","table","increasing"):
    try: print(n, inspect.signature(getattr(m, n)))
    except Exception as e: print(n, "sig?", e)
