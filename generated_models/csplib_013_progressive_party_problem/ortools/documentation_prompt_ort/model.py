from ortools.sat.python import cp_model
import json

# Input data
n_boats = 5  # Number of boats
n_periods = 4  # Number of periods
capacity = [6, 8, 12, 12, 12]  # Capacities of the boats
crew_size = [2, 2, 2, 2, 4]  # Crew sizes of the boats

# Model definition
model = cp_model.CpModel()

# Decision Variables
# is_host[i] = 1 if boat i is a host, 0 otherwise
is_host = [model.NewBoolVar(f'is_host_{i}') for i in range(n_boats)]

# visits[p][g] = h means at period p, guest boat g visits host boat h
# For hosts, visits[p][h] = h (host visits itself)
# Domain: 0..n_boats-1 (host boat indices)
visits = []
for p in range(n_periods):
    period_visits = []
    for g in range(n_boats):
        period_visits.append(model.NewIntVar(0, n_boats - 1, f'visits_p{p}_g{g}'))
    visits.append(period_visits)

# Constraints

# 1) Hosts visit themselves at all periods
for p in range(n_periods):
    for b in range(n_boats):
        # If boat b is host, then visits[p][b] == b
        # If not host, visits[p][b] != b (cannot visit itself)
        model.Add(visits[p][b] == b).OnlyEnforceIf(is_host[b])
        model.Add(visits[p][b] != b).OnlyEnforceIf(is_host[b].Not())

# 2) Guests cannot visit non-host boats
for p in range(n_periods):
    for g in range(n_boats):
        # If g is not host, visits[p][g] must be a host boat
        # If g is host, visits[p][g] == g (already enforced above)
        # So for guests:
        # visits[p][g] in {i | is_host[i] == 1}
        # We enforce: is_host[visits[p][g]] == 1 for guests
        # Create boolean variables for hosts to link
        # We use element constraint: is_host[visits[p][g]] == 1
        # But is_host is bool var list, visits[p][g] is int var
        # Use AddElement
        # Only enforce if g is guest (not host)
        model.AddElement(visits[p][g], is_host, 1).OnlyEnforceIf(is_host[g].Not())

# 3) A guest boat cannot revisit the same host more than once
for g in range(n_boats):
    # Only for guests
    model.AddBoolOr([is_host[g].Not()])  # just to clarify
    # Collect visits of guest g over periods
    guest_visits = [visits[p][g] for p in range(n_periods)]
    # All visits must be different (no revisits)
    # For hosts, visits are always the same (themselves), so no need to enforce
    # For guests, enforce all different
    # Use implication: if g is guest, then all different
    # Create a bool var for guest
    is_guest = is_host[g].Not()
    # Add AllDifferent only if is_guest is true
    # OR-Tools does not support conditional AllDifferent directly,
    # so we enforce pairwise inequality with reification
    for p1 in range(n_periods):
        for p2 in range(p1 + 1, n_periods):
            b = model.NewBoolVar(f'visit_diff_g{g}_p{p1}_p{p2}')
            model.Add(guest_visits[p1] != guest_visits[p2]).OnlyEnforceIf(b)
            model.Add(guest_visits[p1] == guest_visits[p2]).OnlyEnforceIf(b.Not())
            model.AddImplication(is_guest, b)

# 4) Guest crews cannot meet more than once
# Two guest boats cannot be on the same host at the same period more than once
# For each pair of guests (g1, g2), g1 < g2
# For each period p, visits[p][g1] == visits[p][g2] means they meet
# Sum over periods of meetings <= 1
for g1 in range(n_boats):
    for g2 in range(g1 + 1, n_boats):
        # Only for guests
        is_guest1 = is_host[g1].Not()
        is_guest2 = is_host[g2].Not()
        # Create list of bool vars for meetings at each period
        meetings = []
        for p in range(n_periods):
            meet = model.NewBoolVar(f'meet_g{g1}_g{g2}_p{p}')
            model.Add(visits[p][g1] == visits[p][g2]).OnlyEnforceIf(meet)
            model.Add(visits[p][g1] != visits[p][g2]).OnlyEnforceIf(meet.Not())
            # Only consider if both are guests
            # meet => is_guest1 and is_guest2
            model.AddImplication(meet, is_guest1)
            model.AddImplication(meet, is_guest2)
            meetings.append(meet)
        # Sum of meetings <= 1
        model.Add(sum(meetings) <= 1)

# 5) Capacity constraints
# For each boat b and period p:
# total people aboard = crew_size[b] (host crew) + sum of crew_size of guests visiting b at p
# <= capacity[b]
for p in range(n_periods):
    for b in range(n_boats):
        # Sum of crew sizes of guests visiting b at p
        guests_visiting_b = []
        for g in range(n_boats):
            if g == b:
                continue  # host itself
            # Create bool var: guest g visits b at p
            visits_b = model.NewBoolVar(f'visits_b{b}_g{g}_p{p}')
            model.Add(visits[p][g] == b).OnlyEnforceIf(visits_b)
            model.Add(visits[p][g] != b).OnlyEnforceIf(visits_b.Not())
            # Only count if g is guest
            model.AddImplication(visits_b, is_host[g].Not())
            guests_visiting_b.append((visits_b, crew_size[g]))
        # Sum of crew sizes of guests visiting b at p
        # Use linear expression
        total_guests_crew = sum(visits_b * size for visits_b, size in guests_visiting_b)
        # total people aboard = host crew + guests crew <= capacity
        model.Add(total_guests_crew + crew_size[b] <= capacity[b])

# 6) Minimize number of hosts
model.Minimize(sum(is_host))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Extract visits as list of lists: visits[p][g]
    visits_sol = []
    for p in range(n_periods):
        period_visits = []
        for g in range(n_boats):
            period_visits.append(solver.Value(visits[p][g]))
        visits_sol.append(period_visits)
    is_host_sol = [solver.Value(h) for h in is_host]
    solution = {
        'visits': visits_sol,
        'is_host': is_host_sol
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")