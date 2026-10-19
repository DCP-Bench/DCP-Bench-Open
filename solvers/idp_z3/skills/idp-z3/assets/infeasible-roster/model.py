"""Three people work 0 to 3 hours each and must cover 10 hours: impossible."""
from idp_engine import IDP, Theory

KB = """
vocabulary V {
    type Person <: Int
    type Hours <: Int
    need: () -> Int
    work: Person -> Hours
    total: () -> Int
}
theory T: V {
    // the hours worked cover the need exactly
    sum{{ work(p) | p in Person }} = need().
    total() = sum{{ work(p) | p in Person }}.
}
structure S: V {
    Person := {0..2}.
    Hours := {0..3}.
    need := 10.
}
"""
kb = IDP.from_str(KB)

# expand() reports infeasibility as a message string, not as an exception.
models = list(Theory(*kb.get_blocks("T, S")).expand(max=1, timeout_seconds=10))
print("expand:", repr(models[-1]))
if models == ["No models."]:
    print("status: infeasible")

# optimize() raises instead, with the same message for "infeasible" and "z3 gave up".
try:
    Theory(*kb.get_blocks("T, S")).optimize("total()", minimize=True)
except AssertionError as error:
    print("optimize:", error)
