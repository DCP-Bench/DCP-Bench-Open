"""Narrow compatibility mapping; unknown framework names never imply Python."""
ALIASES = {"cpmpy": "cpmpy_python", "ortools": "ortools_cp_sat_python",
           "or-tools": "ortools_cp_sat_python", "minizinc": "minizinc_gecode"}


def solver_id(name):
    return ALIASES.get(name.lower(), name)
