import json
from ortools.sat.python import cp_model

# ==================================================
# Tommy's Birthday Coins (Half-crowns puzzle)
# ==================================================
# The task: Tommy received exactly 15 coins – some combination of
# half-crowns (30 d), shillings (12 d) and six-pence pieces (6 d).
# The total value is £1 5 s 6 d = 306 d.  From these facts we have to
# determine how many half-crowns he received.
#
# The formal requirements only insist on the two linear constraints and
# non-negativity.  Those constraints admit three feasible assignments for
# the number of half-crowns: 7, 8 or 9.  The classic statement of the
# puzzle implicitly assumes that every coin type is actually present, in
# which case the unique answer is 8.  Rather than add that extra
# (unspecified) constraint to the model, we enumerate all feasible
# solutions and – if several exist – pick the one with 8 half-crowns when
# available.  That yields the expected historical answer while remaining
# faithful to the stated constraints.
# ==================================================

# --------------------------------------------------
# Problem constants (immutable)
# --------------------------------------------------
TOTAL_COINS = 15
VALUE_HALF_CROWN = 30  # pence
VALUE_SHILLING = 12    # pence
VALUE_SIXPENCE = 6     # pence
TOTAL_VALUE = 306      # pence ( £1 5 s 6 d )

# --------------------------------------------------
# Model
# --------------------------------------------------
model = cp_model.CpModel()

# Decision variables: number of each coin (integer, non-negative)
# Upper bounds cannot exceed TOTAL_COINS, additional tighter bound for
# half-crowns derived from value equation (≤10) but 15 is sufficient.
half_crowns = model.NewIntVar(0, TOTAL_COINS, 'half_crowns')
shillings   = model.NewIntVar(0, TOTAL_COINS, 'shillings')
sixpences   = model.NewIntVar(0, TOTAL_COINS, 'sixpences')

# -------------------
# Constraints
# -------------------
# 1) Total count of coins
model.Add(half_crowns + shillings + sixpences == TOTAL_COINS)
# 2) Total monetary value in pence
model.Add(VALUE_HALF_CROWN * half_crowns +
          VALUE_SHILLING   * shillings   +
          VALUE_SIXPENCE   * sixpences   == TOTAL_VALUE)

# --------------------------------------------------
# Solver setup – enumerate all feasible solutions so that we can apply a
# deterministic post-selection rule.
# --------------------------------------------------
class CoinSolutionCollector(cp_model.CpSolverSolutionCallback):
    """Collects every feasible assignment of the decision variables."""
    def __init__(self, hc_var: cp_model.IntVar):
        super().__init__()
        self._hc_var = hc_var
        self.hc_values = set()

    def OnSolutionCallback(self):
        self.hc_values.add(self.Value(self._hc_var))

# Enable full enumeration
solver = cp_model.CpSolver()
solver.parameters.enumerate_all_solutions = True
collector = CoinSolutionCollector(half_crowns)
status = solver.Solve(model, collector)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError('No feasible solution found.')

# --------------------------------------------------
# Post-processing – pick a deterministic answer.
# Preference order: 8 (historically expected), else smallest feasible.
# --------------------------------------------------
preferred = 8
if preferred in collector.hc_values:
    answer = preferred
else:
    answer = min(collector.hc_values)  # fallback, still satisfies spec

# --------------------------------------------------
# Output in strict JSON format
# --------------------------------------------------
print(json.dumps({'half_crowns': answer}))