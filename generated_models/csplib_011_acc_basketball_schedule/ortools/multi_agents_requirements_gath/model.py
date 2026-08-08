import json
import os
from ortools.sat.python import cp_model

# ------------------------------------------------------------
# 1997/98 ACC men’s basketball – double round-robin timetable
# ------------------------------------------------------------
# A pure feasibility model: any schedule that fulfils every rule is OK.
# ------------------------------------------------------------

# -------------- fixed input (exactly as provided) ------------
# The statement literally says:  n_teams = 9 n_days = 18
n_teams = 9
n_days  = 18
teams    = range(n_teams)

# symbolic names for readability
CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)

# ------------------------------------------------------------
# Static data
# ------------------------------------------------------------
weekend_idx      = [1, 3, 5, 7, 9, 11, 13, 15, 17]   # even dates in 0-base
first5_weekends  = [1, 3, 5, 7, 9]

# mirroring pairs – already 0-based
mirror_pairs = [(0, 7), (1, 8), (2, 11), (3, 12), (4, 13),
                (5, 14), (6, 15), (9, 16), (10, 17)]

# rival dictionary  (-1 = no rival)
rival = [-1] * n_teams
rival[CLEM] = GT;   rival[GT]   = CLEM
rival[DUKE] = UNC;  rival[UNC]  = DUKE
rival[NCST] = WAKE; rival[WAKE] = NCST
rival[UMD]  = UVA;  rival[UVA]  = UMD
# FSU has no traditional rival

# Pairings that must occur at least once in dates 11-18 (unordered)
special_pairs = [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]

# ------------------------------------------------------------
# Model
# ------------------------------------------------------------
model = cp_model.CpModel()

# Oriented HOME variables  H[t,s,d]  – t plays HOME vs s on date d (t≠s)
home = {}
for t in teams:
    for s in teams:
        if t == s:
            continue
        for d in range(n_days):
            home[(t, s, d)] = model.NewBoolVar(f"H_{t}_{s}_{d}")

# Bye variables
bye = {(t, d): model.NewBoolVar(f"B_{t}_{d}") for t in teams for d in range(n_days)}

# Derived single-bit indicators  isHome / isAway per team & date
is_home = {}
is_away = {}
for t in teams:
    for d in range(n_days):
        ih = model.NewBoolVar(f"isH_{t}_{d}")
        ia = model.NewBoolVar(f"isA_{t}_{d}")
        is_home[(t, d)] = ih
        is_away[(t, d)] = ia

        # exactly one status each day
        model.Add(ih + ia + bye[(t, d)] == 1)

        # link to oriented vars
        model.Add(ih == sum(home[(t, s, d)] for s in teams if s != t))
        model.Add(ia == sum(home[(s, t, d)] for s in teams if s != t))

# At most one orientation for every unordered pair & date
for t in teams:
    for s in teams:
        if t < s:
            for d in range(n_days):
                model.Add(home[(t, s, d)] + home[(s, t, d)] <= 1)

# ---------------- round-robin totals & daily balance ----------------
# 4 homes, 4 aways, 1 bye per date
for d in range(n_days):
    model.Add(sum(is_home[(t, d)] for t in teams) == 4)
    model.Add(sum(is_away[(t, d)] for t in teams) == 4)
    model.Add(sum(bye[(t, d)]    for t in teams) == 1)

# each unordered pair meets twice, once at each venue
for t in teams:
    for s in teams:
        if t < s:
            model.Add(sum(home[(t, s, d)] for d in range(n_days)) == 1)
            model.Add(sum(home[(s, t, d)] for d in range(n_days)) == 1)

# exactly two byes per team
for t in teams:
    model.Add(sum(bye[(t, d)] for d in range(n_days)) == 2)

# ---------------- mirroring ----------------
for r1, r2 in mirror_pairs:
    for t in teams:
        model.Add(bye[(t, r1)] == bye[(t, r2)])
    for t in teams:
        for s in teams:
            if t < s:
                model.Add(home[(t, s, r1)] == home[(s, t, r2)])
                model.Add(home[(s, t, r1)] == home[(t, s, r2)])

# ---------------- pattern constraints ----------------
for t in teams:
    # max 2 consecutive homes / aways
    for d in range(n_days - 2):
        model.Add(is_home[(t, d)] + is_home[(t, d+1)] + is_home[(t, d+2)] <= 2)
        model.Add(is_away[(t, d)] + is_away[(t, d+1)] + is_away[(t, d+2)] <= 2)
    # max 4 consecutive (Home ∨ Bye)
    for d in range(n_days - 4):
        model.Add(sum(is_home[(t, d+k)] + bye[(t, d+k)] for k in range(5)) <= 4)
    # max 3 consecutive (Away ∨ Bye)
    for d in range(n_days - 3):
        model.Add(sum(is_away[(t, d+k)] + bye[(t, d+k)] for k in range(4)) <= 3)

    # weekend quotas 4-4-1
    model.Add(sum(is_home[(t, d)] for d in weekend_idx) == 4)
    model.Add(sum(is_away[(t, d)] for d in weekend_idx) == 4)
    model.Add(sum(bye[(t, d)]    for d in weekend_idx) == 1)

    # at least two (Home ∨ Bye) among first five weekends
    model.Add(sum(is_home[(t, d)] + bye[(t, d)] for d in first5_weekends) >= 2)

# no two final aways (dates 17 & 18 → indices 16,17)
for t in teams:
    model.Add(is_away[(t, 16)] + is_away[(t, 17)] <= 1)

# ---------------- helper: plays_vs[t,o,d] ----------------
plays_vs = {}
for t in teams:
    for o in teams:
        if t == o:
            continue
        for d in range(n_days):
            v = model.NewBoolVar(f"P_{t}_{o}_{d}")
            plays_vs[(t, o, d)] = v
            model.Add(v == home[(t, o, d)] + home[(o, t, d)])

# ---------------- opponent-sequence constraints ----------------
# (a) no consecutive AWAY at UNC and Duke (either order)
for t in teams:
    if t in (UNC, DUKE):
        continue
    for d in range(n_days - 1):
        model.Add(home[(UNC, t, d)] + home[(DUKE, t, d+1)] <= 1)
        model.Add(home[(DUKE, t, d)] + home[(UNC, t, d+1)] <= 1)

# (b) forbid window of 3 consecutive dates containing ALL THREE opponents {UNC,DUKE,WAKE}
for t in teams:
    for d in range(n_days - 2):
        # sums of appearances of each specific opponent in the 3-day window
        sumU = plays_vs[(t, UNC,  d)] + plays_vs[(t, UNC,  d+1)] + plays_vs[(t, UNC,  d+2)]
        sumD = plays_vs[(t, DUKE, d)] + plays_vs[(t, DUKE, d+1)] + plays_vs[(t, DUKE, d+2)]
        sumW = plays_vs[(t, WAKE, d)] + plays_vs[(t, WAKE, d+1)] + plays_vs[(t, WAKE, d+2)]

        bU = model.NewBoolVar(f"pU_{t}_{d}")
        bD = model.NewBoolVar(f"pD_{t}_{d}")
        bW = model.NewBoolVar(f"pW_{t}_{d}")

        # channel  presence <-> sum ≥ 1   (both directions)
        model.Add(bU <= sumU)
        model.Add(sumU <= 3 * bU)
        model.Add(bD <= sumD)
        model.Add(sumD <= 3 * bD)
        model.Add(bW <= sumW)
        model.Add(sumW <= 3 * bW)

        # forbid all three present
        model.Add(bU + bD + bW <= 2)

# ---------------- last-date (date 18 / idx17) rival rule ----------------
for t in teams:
    if t == FSU:
        continue  # rule exempt
    r_terms = [bye[(t, 17)]]
    if rival[t] != -1:
        r = rival[t]
        r_terms.extend([home[(t, r, 17)], home[(r, t, 17)]])
    r_terms.extend([home[(t, FSU, 17)], home[(FSU, t, 17)]])
    model.Add(sum(r_terms) == 1)

# ---------------- mandatory fixtures ----------------
# UNC vs Duke on dates 11 (idx10) and 18 (idx17)
model.Add(home[(UNC, DUKE, 10)] + home[(DUKE, UNC, 10)] == 1)
model.Add(home[(UNC, DUKE, 17)] + home[(DUKE, UNC, 17)] == 1)

# UNC vs Clemson on date 2 (idx1)
model.Add(home[(UNC, CLEM, 1)] + home[(CLEM, UNC, 1)] == 1)

# special pairs at least once in dates 11-18
for u, v in special_pairs:
    model.Add(sum(home[(u, v, d)] + home[(v, u, d)] for d in range(10, 18)) >= 1)

# ---------------- explicit fixed / forbidden events ----------------
model.Add(bye[(DUKE, 15)] == 1)         # Duke bye date 16 (idx15)
model.Add(bye[(WAKE, 0)] == 1)          # Wake bye date 1
model.Add(is_home[(WAKE, 16)] == 0)     # Wake not home date 17 (idx16)

for t in (CLEM, DUKE, UMD, WAKE):       # no away on date 18 (idx17)
    model.Add(is_away[(t, 17)] == 0)
for t in (CLEM, FSU, GT, WAKE):         # no away on date 1 (idx0)
    model.Add(is_away[(t, 0)] == 0)

model.Add(bye[(FSU, 17)] == 0)          # FSU not bye last date
model.Add(bye[(NCST, 17)] == 0)         # NCSt not bye last date
model.Add(bye[(UNC, 0)] == 0)           # UNC no bye first date

# ------------------------------------------------------------
# Solve
# ------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 300.0  # 5-minute safety cap
solver.parameters.num_search_workers  = min(8, os.cpu_count() or 1)
result = solver.Solve(model)

if result not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No feasible timetable could be produced within the time limit.")

# ------------------------------------------------------------
# Extract solution into required arrays
# ------------------------------------------------------------
config = [[-1] * n_days for _ in teams]
where  = [["B"] * n_days for _ in teams]  # default bye – overwritten for games

for t in teams:
    for d in range(n_days):
        if solver.Value(bye[(t, d)]) == 1:
            continue  # already filled with (-1, 'B')
        # locate opponent & orientation
        for s in teams:
            if t == s:
                continue
            if solver.Value(home[(t, s, d)]) == 1:
                config[t][d] = s
                where[t][d]  = "H"
                break
            if solver.Value(home[(s, t, d)]) == 1:
                config[t][d] = s
                where[t][d]  = "A"
                break
        else:
            raise RuntimeError(f"Extraction error: team {t} on date {d} has no opponent.")

# ------------------------------------------------------------
# Output JSON
# ------------------------------------------------------------
print(json.dumps({"config": config, "where": where}))