from ortools.sat.python import cp_model
import json

# Input data
n = 8  # Number of words to find
length = 8
alphabet = ['A', 'C', 'G', 'T']
# Map letters to integers for easier handling
letter_to_int = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
int_to_letter = {v: k for k, v in letter_to_int.items()}

# Complement mapping: A<->T, C<->G
complement_map = {0: 3, 1: 2, 2: 1, 3: 0}

model = cp_model.CpModel()

# Decision variables: words[i][j] in {0,1,2,3} representing letters
words = []
for i in range(n):
    word = [model.NewIntVar(0, 3, f'word_{i}_{j}') for j in range(length)]
    words.append(word)

# Constraint 1: Each word has exactly 4 symbols from {C,G} (i.e. letters 1 or 2)
for i in range(n):
    # Create boolean variables indicating if position j is C or G
    cg_bools = []
    for j in range(length):
        is_cg = model.NewBoolVar(f'is_cg_{i}_{j}')
        # is_cg == 1 if words[i][j] in {1,2}
        model.Add(words[i][j] == 1).OnlyEnforceIf(is_cg)
        model.Add(words[i][j] != 1).OnlyEnforceIf(is_cg.Not())
        is_g = model.NewBoolVar(f'is_g_{i}_{j}')
        model.Add(words[i][j] == 2).OnlyEnforceIf(is_g)
        model.Add(words[i][j] != 2).OnlyEnforceIf(is_g.Not())
        # is_cg = is_c or is_g
        model.AddBoolOr([is_cg, is_g]).OnlyEnforceIf(is_cg)
        model.AddBoolAnd([is_cg.Not(), is_g.Not()]).OnlyEnforceIf(is_cg.Not())
        # Actually, we can just say is_cg = is_c or is_g
        # But to simplify, we can just define is_cg as (words[i][j] in {1,2})
        # So we can define is_cg as a bool var and add:
        # is_cg == (words[i][j] == 1 or words[i][j] == 2)
        # We can do this by:
        # is_cg == max(is_c, is_g)
        # But OR-Tools does not have max for bools, so we do:
        # is_cg >= is_c, is_cg >= is_g, is_cg <= is_c + is_g
        # Let's do that:
        # But we already defined is_cg as words[i][j]==1, so let's redefine:
        # Let's remove previous and do simpler:
    # Let's redo this constraint more simply:
    # We create two bools: is_c and is_g, then is_cg = is_c or is_g
    # Then sum is_cg == 4
    # Let's do it cleanly:
    # Remove previous and do:
    pass

# Re-implement constraint 1 cleanly:
for i in range(n):
    is_cg = []
    for j in range(length):
        b = model.NewBoolVar(f'is_cg_{i}_{j}')
        # b == 1 if words[i][j] in {1,2}
        model.Add(words[i][j] == 1).OnlyEnforceIf(b)
        model.Add(words[i][j] != 1).OnlyEnforceIf(b.Not())
        b2 = model.NewBoolVar(f'is_g_{i}_{j}')
        model.Add(words[i][j] == 2).OnlyEnforceIf(b2)
        model.Add(words[i][j] != 2).OnlyEnforceIf(b2.Not())
        # b == b or b2
        # So b == max(b, b2)
        # We enforce b >= b2 and b <= b + b2
        model.AddBoolOr([b, b2]).OnlyEnforceIf(b)
        model.AddBoolAnd([b.Not(), b2.Not()]).OnlyEnforceIf(b.Not())
        # Actually, the above is redundant, we want b == (b or b2)
        # So we can do:
        # b >= b2
        model.AddImplication(b2, b)
        # b <= b + b2 is always true
        # Also b >= b (trivial)
        # To ensure b == b or b2, we add:
        model.AddBoolOr([b, b2]).OnlyEnforceIf(b)
        model.AddBoolAnd([b.Not(), b2.Not()]).OnlyEnforceIf(b.Not())
        # But this is complicated, simpler is:
        # b == 1 if words[i][j] in {1,2}
        # So we can do:
        # b == 1 if words[i][j] == 1 or words[i][j] == 2
        # So b == (words[i][j] == 1) or (words[i][j] == 2)
        # We can do:
        # b == b_cg
        # So let's just define b as a bool var and add:
        # b == (words[i][j] == 1 or words[i][j] == 2)
        # This can be done by:
        # b == b_c or b_g
        # So we create b_c and b_g:
        b_c = model.NewBoolVar(f'is_c_{i}_{j}')
        b_g = model.NewBoolVar(f'is_g_{i}_{j}')
        model.Add(words[i][j] == 1).OnlyEnforceIf(b_c)
        model.Add(words[i][j] != 1).OnlyEnforceIf(b_c.Not())
        model.Add(words[i][j] == 2).OnlyEnforceIf(b_g)
        model.Add(words[i][j] != 2).OnlyEnforceIf(b_g.Not())
        model.AddBoolOr([b_c, b_g]).OnlyEnforceIf(b)
        model.AddBoolAnd([b_c.Not(), b_g.Not()]).OnlyEnforceIf(b.Not())
        is_cg.append(b)
    model.Add(sum(is_cg) == 4)

# Constraint 2: Each pair of distinct words differ in at least 4 positions
for i in range(n):
    for j in range(i + 1, n):
        diffs = []
        for k in range(length):
            diff = model.NewBoolVar(f'diff_{i}_{j}_{k}')
            model.Add(words[i][k] != words[j][k]).OnlyEnforceIf(diff)
            model.Add(words[i][k] == words[j][k]).OnlyEnforceIf(diff.Not())
            diffs.append(diff)
        model.Add(sum(diffs) >= 4)

# Constraint 3: For each pair x,y (including x=y), x^R and y^C differ in at least 4 positions
# x^R is reverse of x
# y^C is complement of y
for i in range(n):
    for j in range(n):
        diffs_rc = []
        for k in range(length):
            # x^R[k] = words[i][length-1-k]
            # y^C[k] = complement(words[j][k])
            diff = model.NewBoolVar(f'diff_rc_{i}_{j}_{k}')
            # We need to check if words[i][length-1-k] != complement(words[j][k])
            # Since complement is a function, we create an intermediate variable for complement
            yj_k = words[j][k]
            comp_yj_k = model.NewIntVar(0, 3, f'comp_{j}_{k}')
            # comp_yj_k == complement_map[yj_k]
            # We use AddElement to model complement
            model.AddElement(yj_k, [complement_map[0], complement_map[1], complement_map[2], complement_map[3]], comp_yj_k)
            model.Add(words[i][length - 1 - k] != comp_yj_k).OnlyEnforceIf(diff)
            model.Add(words[i][length - 1 - k] == comp_yj_k).OnlyEnforceIf(diff.Not())
            diffs_rc.append(diff)
        model.Add(sum(diffs_rc) >= 4)

# Objective: maximize the number of words found
# But n is fixed input, so just find feasible solution with n words

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 60.0  # Limit time to 60 seconds

status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution_words = []
    for i in range(n):
        w = ''.join(int_to_letter[solver.Value(words[i][j])] for j in range(length))
        solution_words.append(w)
    solution = {'words': solution_words}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")