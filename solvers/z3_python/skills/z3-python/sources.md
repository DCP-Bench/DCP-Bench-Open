# Sources for `z3-python`

Documentation this skill's instructions were written from. Add an entry
whenever a claim here comes from a specific page or version.

- <https://z3prover.github.io/api/html/namespacez3py.html> — Z3 Python API reference, accessed 2026-09-10
- <https://microsoft.github.io/z3guide/docs/logic/intro/> — Z3 guide, accessed 2026-09-10
- <https://github.com/Z3Prover/z3> — z3-solver 5.1.0.0, the version pinned in the integration image

Every entry in the idiom table and every "verified" gotcha was checked by
running Z3 5.1.0, not taken from documentation alone:

- `Distinct`, `Sum`, `Product`, `If`, `And`, `Or`, `Not`, `Implies`, `Xor`,
  `PbEq`, `PbLe`, `PbGe`, `AtMost`, `AtLeast`, `Select`, `Store`, `Array`,
  `IntVector`, `BoolVector` and `Abs` all resolve in the `z3` namespace.
  `Abs` does exist, contrary to a common assumption.
- `Max`, `Min`, `Element` and `AllDifferent` do **not** exist; `Distinct` is the
  all-different constraint, and max/min need the `If`-reduce idiom, which was
  checked to return 9 and 1 over `[3, 9, 1, 7]`.
- Python `max`, `min`, `any` and `all` raise `Z3Exception: Symbolic expressions
  cannot be cast to concrete Boolean values`. Python `sum` does not.
- Division and modulo were compared against Python directly: Z3 gives
  `7 / -2 = -3` and `7 % -2 = 1`; Python gives `-4` and `-1`. `-7 / 2` and
  `-7 % 2` agree at `-4` and `1`.
- `Optimize.lower(handle) == Optimize.upper(handle)` is what proves an optimum,
  which is how the runner establishes optimality rather than trusting `check()`.
