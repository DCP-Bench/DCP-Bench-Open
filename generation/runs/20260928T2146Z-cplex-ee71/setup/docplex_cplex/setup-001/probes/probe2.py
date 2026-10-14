from docplex.mp.model import Model
import docplex.mp.utils as u
print([n for n in dir(u) if 'Exceed' in n or 'Error' in n or 'Exception' in n])
m = Model(); x = m.integer_var_list(1001, ub=3); m.add(m.sum(x) >= 1)
try:
    m.solve()
except Exception as e:
    print(type(e).__module__, type(e).__name__, [c.__name__ for c in type(e).__mro__])
m = Model(); a = m.integer_var(-3, 3, name="a"); f = m.abs(a); print(type(f).__name__, hasattr(f, "as_var"), [n for n in dir(f) if 'var' in n.lower()][:10])
m.add(a == -2); s = m.solve(); print("abs value", f.solution_value, f.as_var.vartype.short_name if hasattr(f, 'as_var') else None)
x = m.integer_var(0, 3, name="x"); print(x.vartype.short_name, m.binary_var().vartype.short_name, m.continuous_var().vartype.short_name, x.is_integer(), x.lb, x.ub)
print("remove_objective", hasattr(m, "remove_objective"), "add_range", hasattr(m, "add_range"), "number_of_constraints", m.number_of_constraints, m.number_of_variables)
m2 = Model(); y = m2.continuous_var(0, 1); m2.add(y >= 0.5); m2.minimize(y); s = m2.solve(); print("LP", m2.solve_details.status_code, m2.solve_details.status)
