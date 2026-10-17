# Graph colouring: give each vertex one colour so that adjacent vertices differ, using as few
# colours as possible. The graph is the Petersen graph (10 vertices, 15 edges).
# Method: a binary per vertex and colour, and a binary per colour that says whether it is used.
# The number of colours offered comes from the data: max degree + 1 always suffices.
import mip

edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
         (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
         (5, 7), (7, 9), (9, 6), (6, 8), (8, 5)]
vertices = sorted({v for e in edges for v in e})
degree = {v: sum(v in e for e in edges) for v in vertices}
colours = range(max(degree.values()) + 1)

m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
m.verbose = 0
m.max_mip_gap = 0.0
m.max_mip_gap_abs = 0.0
x = {(v, k): m.add_var(f"x_{v}_{k}", var_type=mip.BINARY) for v in vertices for k in colours}
used = {k: m.add_var(f"used_{k}", var_type=mip.BINARY) for k in colours}

# every vertex gets exactly one colour
for v in vertices:
    m += mip.xsum(x[v, k] for k in colours) == 1

# adjacent vertices never share a colour
for (u, w) in edges:
    for k in colours:
        m += x[u, k] + x[w, k] <= 1

# a colour counts as used when some vertex has it
for v in vertices:
    for k in colours:
        m += used[k] >= x[v, k]

m.objective = mip.xsum(used.values())
status = m.optimize(max_seconds=60)
if status == mip.OptimizationStatus.OPTIMAL:
    print("Colours used:", round(m.objective_value))
    for v in vertices:
        colour = next(k for k in colours if x[v, k].x > 0.5)
        print(f"  vertex {v}: colour {colour}")
else:
    print("Status:", status.name)
