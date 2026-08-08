import json
from ortools.sat.python import cp_model

# -----------------------------
# Data (fixed indices used later)
# -----------------------------
# Index mapping (1..5) required by the statement
# Children indices
BERNICE = 1
CARL    = 2
DEBBY   = 3
SAMMY   = 4
TED     = 5

# Country indices
ETHIOPIA   = 1
KAZAKHSTAN = 2
LITHUANIA  = 3
MOROCCO    = 4
YEMEN      = 5

# Story indices
BURNING_BUSH      = 1
CAPTIVITY         = 2
MOSES_YOUTH       = 3
PASSOVER          = 4
TEN_COMMANDMENTS  = 5

# Age indices and their numeric values (index 1..5)
AGE_VALUES = {
    1: 3,
    2: 5,
    3: 7,
    4: 8,
    5: 10,
}

N = 5  # number of positions / children

model = cp_model.CpModel()

# -----------------------------
# Decision variables (per position 0..4)
# -----------------------------
children  = [model.NewIntVar(1, N, f'child_{p}')     for p in range(N)]
ages_idx  = [model.NewIntVar(1, N, f'age_idx_{p}')   for p in range(N)]  # 1..5 index
countries = [model.NewIntVar(1, N, f'country_{p}')  for p in range(N)]
stories   = [model.NewIntVar(1, N, f'story_{p}')    for p in range(N)]

# Helper: numeric age value per position (3,5,7,8,10)
age_values = [model.NewIntVar(min(AGE_VALUES.values()),
                              max(AGE_VALUES.values()), f'age_val_{p}')
              for p in range(N)]

# -----------------------------
# Global permutation constraints
# -----------------------------
model.AddAllDifferent(children)
model.AddAllDifferent(ages_idx)
model.AddAllDifferent(countries)
model.AddAllDifferent(stories)

# Link age index (1..5) to its numeric value via Element
for p in range(N):
    # Convert 1..5 -> 0..4 for Element
    idx0 = model.NewIntVar(0, N - 1, f'idx0_{p}')
    model.Add(idx0 + 1 == ages_idx[p])
    model.AddElement(idx0, [3, 5, 7, 8, 10], age_values[p])

# -----------------------------
# Utility: create equality indicator literals
# -----------------------------

def equals_lit(var, const, name):
    """Return a BoolVar that is true iff var == const."""
    b = model.NewBoolVar(name)
    model.Add(var == const).OnlyEnforceIf(b)
    model.Add(var != const).OnlyEnforceIf(b.Not())
    return b

# Pre-compute needed equality literals for every position
is_debby    = [equals_lit(children[p], DEBBY,    f'is_debby_{p}')    for p in range(N)]
is_bernice  = [equals_lit(children[p], BERNICE,  f'is_bernice_{p}')  for p in range(N)]
is_sammy    = [equals_lit(children[p], SAMMY,    f'is_sammy_{p}')    for p in range(N)]
is_ted      = [equals_lit(children[p], TED,      f'is_ted_{p}')      for p in range(N)]

is_passover = [equals_lit(stories[p], PASSOVER, f'is_passover_{p}') for p in range(N)]
is_moses    = [equals_lit(stories[p], MOSES_YOUTH, f'is_moses_{p}') for p in range(N)]

is_yemen    = [equals_lit(countries[p], YEMEN,     f'is_yemen_{p}')    for p in range(N)]
is_ethiopia = [equals_lit(countries[p], ETHIOPIA,  f'is_ethiopia_{p}') for p in range(N)]
is_morocco  = [equals_lit(countries[p], MOROCCO,   f'is_morocco_{p}')  for p in range(N)]

# -----------------------------
# Clue C1: Debby -> Lithuania
# -----------------------------
for p in range(N):
    model.Add(countries[p] == LITHUANIA).OnlyEnforceIf(is_debby[p])

# -----------------------------
# Clue C2: Passover is two years older than Bernice
# -----------------------------
for i in range(N):
    for j in range(N):
        cond = model.NewBoolVar(f'passover_vs_bernice_{i}_{j}')
        # cond <=> (is_passover[i] AND is_bernice[j])
        model.AddBoolAnd([is_passover[i], is_bernice[j]]).OnlyEnforceIf(cond)
        model.AddBoolOr([is_passover[i].Not(), is_bernice[j].Not(), cond])
        # When cond is true enforce age difference
        model.Add(age_values[i] - age_values[j] == 2).OnlyEnforceIf(cond)

# -----------------------------
# Clue C3: Yemen child younger than Ethiopia child
# -----------------------------
for i in range(N):
    for j in range(N):
        cond = model.NewBoolVar(f'yemen_vs_ethiopia_{i}_{j}')
        model.AddBoolAnd([is_yemen[i], is_ethiopia[j]]).OnlyEnforceIf(cond)
        model.AddBoolOr([is_yemen[i].Not(), is_ethiopia[j].Not(), cond])
        # age_yemen +1 <= age_ethiopia  (strictly younger)
        model.Add(age_values[i] + 1 <= age_values[j]).OnlyEnforceIf(cond)

# -----------------------------
# Clue C4: Morocco child three years older than Ted
# -----------------------------
for i in range(N):
    for j in range(N):
        cond = model.NewBoolVar(f'morocco_vs_ted_{i}_{j}')
        model.AddBoolAnd([is_morocco[i], is_ted[j]]).OnlyEnforceIf(cond)
        model.AddBoolOr([is_morocco[i].Not(), is_ted[j].Not(), cond])
        model.Add(age_values[i] - age_values[j] == 3).OnlyEnforceIf(cond)

# -----------------------------
# Clue C5: Sammy three years older than Moses's youth storyteller
# -----------------------------
for i in range(N):
    for j in range(N):
        cond = model.NewBoolVar(f'sammy_vs_moses_{i}_{j}')
        model.AddBoolAnd([is_sammy[i], is_moses[j]]).OnlyEnforceIf(cond)
        model.AddBoolOr([is_sammy[i].Not(), is_moses[j].Not(), cond])
        model.Add(age_values[i] - age_values[j] == 3).OnlyEnforceIf(cond)

# -----------------------------
# Solve model
# -----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30  # safety limit
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError('No solution found')

# Extract results as required lists (1..5 indices)
result_children  = [int(solver.Value(children[p]))  for p in range(N)]
result_ages      = [int(solver.Value(ages_idx[p])) for p in range(N)]
result_countries = [int(solver.Value(countries[p])) for p in range(N)]
result_stories   = [int(solver.Value(stories[p]))  for p in range(N)]

output = {
    'countries': result_countries,
    'children':  result_children,
    'stories':   result_stories,
    'ages':      result_ages,
}

print(json.dumps(output))
