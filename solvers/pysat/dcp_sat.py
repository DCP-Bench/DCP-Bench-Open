"""The modelling surface for the pysat integration. Ships inside the image.

A SAT solver has no integers and no arithmetic, so everything a problem needs
has to become Boolean variables and clauses. This module does that encoding once
so a submission can state the problem instead:

- `Sat.int` gives an integer variable under a direct (one-hot) encoding, with
  the exactly-one clauses already posted, so `x == v` is a literal and costs
  nothing to ask for.
- Linear constraints go through pseudo-Boolean encodings over those one-hot
  literals, with the weight of "x takes value v" being v itself. Negative values
  and negative coefficients are shifted to non-negative weights first, because
  the underlying pypblib encoders want them that way.
- Cardinality over plain literals goes through `pysat.card`.

The submission never sees a clause unless it wants to; `Sat.clause` is there for
when hand-written logic is clearer than a helper.
"""
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.pb import PBEnc


class IntVar:
    """An integer variable under a direct encoding.

    `lits[i]` is true exactly when the variable takes `values[i]`. Exactly one of
    them is true, which `Sat.int` posts at construction.
    """

    def __init__(self, values, lits):
        self.values = list(values)
        self.lits = list(lits)

    def literal(self, value):
        """The literal meaning `self == value`, or None when out of domain."""
        try:
            return self.lits[self.values.index(value)]
        except ValueError:
            return None

    def read(self, truth):
        """The value this variable takes in a solution, given its true literals."""
        for value, lit in zip(self.values, self.lits):
            if lit in truth:
                return value
        raise ValueError("no value is true for an integer variable; exactly-one was lost")

    def terms(self, coefficient=1):
        """(literal, weight) pairs whose sum is `coefficient * self`."""
        return [(lit, coefficient * value) for lit, value in zip(self.lits, self.values)]


class Sat:
    """Builds the CNF a submission describes."""

    def __init__(self):
        self.pool = IDPool()
        self.clauses = []

    # --- variables ---------------------------------------------------------

    def bool(self):
        """A fresh Boolean variable, returned as a positive literal."""
        return self.pool.id()

    def bools(self, n):
        return [self.bool() for _ in range(n)]

    def bool_grid(self, rows, cols):
        return [self.bools(cols) for _ in range(rows)]

    def always(self):
        """A literal fixed true, for places that want one."""
        lit = self.bool()
        self.clauses.append([lit])
        return lit

    def never(self):
        return -self.always()

    def int(self, lo, hi):
        """An integer variable on `[lo, hi]`, one-hot encoded."""
        if lo > hi:
            raise ValueError(f"empty domain [{lo}, {hi}]")
        return self.int_from(range(lo, hi + 1))

    def int_from(self, values):
        """An integer variable whose domain is exactly `values`."""
        values = list(dict.fromkeys(values))
        if not values:
            raise ValueError("an integer variable needs at least one value")
        lits = self.bools(len(values))
        # exactly one value holds
        self.clauses.append(list(lits))
        self.clauses.extend(CardEnc.atmost(lits=lits, bound=1, vpool=self.pool,
                                           encoding=EncType.pairwise).clauses)
        return IntVar(values, lits)

    def ints(self, n, lo, hi):
        return [self.int(lo, hi) for _ in range(n)]

    def int_grid(self, rows, cols, lo, hi):
        return [self.ints(cols, lo, hi) for _ in range(rows)]

    def constant(self, value):
        """An integer variable fixed to `value`."""
        return self.int_from([value])

    # --- raw clauses -------------------------------------------------------

    def clause(self, lits):
        """At least one of these literals is true."""
        self.clauses.append(list(lits))

    def implies(self, antecedent, consequent):
        """`antecedent -> consequent`, both plain literals."""
        self.clauses.append([-antecedent, consequent])

    def iff(self, left, right):
        """`left <-> right`, both plain literals."""
        self.clauses.append([-left, right])
        self.clauses.append([left, -right])

    # --- cardinality over literals ----------------------------------------

    def at_most(self, lits, bound):
        lits = list(lits)
        if bound >= len(lits):
            return
        if bound < 0:
            self.clauses.append([])
            return
        self.clauses.extend(CardEnc.atmost(lits=lits, bound=bound, vpool=self.pool,
                                           encoding=EncType.seqcounter).clauses)

    def at_least(self, lits, bound):
        lits = list(lits)
        if bound <= 0:
            return
        if bound > len(lits):
            self.clauses.append([])
            return
        self.clauses.extend(CardEnc.atleast(lits=lits, bound=bound, vpool=self.pool,
                                            encoding=EncType.seqcounter).clauses)

    def exactly(self, lits, bound):
        self.at_most(lits, bound)
        self.at_least(lits, bound)

    # --- linear constraints over integer variables ------------------------

    def _linear(self, terms):
        """Flatten `(coefficient, IntVar)` pairs into non-negative PB weights.

        The encoders want non-negative weights, so each term is shifted down by
        its own minimum and the shift is handed back to move the bound instead.
        """
        lits, weights, offset = [], [], 0
        for coefficient, var in terms:
            pairs = var.terms(coefficient)
            least = min(weight for _, weight in pairs)
            offset += least
            for lit, weight in pairs:
                if weight != least:
                    lits.append(lit)
                    weights.append(weight - least)
        return lits, weights, offset

    def _pb(self, terms, bound, kind):
        lits, weights, offset = self._linear(terms)
        target = bound - offset
        if not lits:
            # Every term is fixed, so the constraint is decided already.
            holds = {"le": 0 <= target, "ge": 0 >= target, "eq": target == 0}[kind]
            if not holds:
                self.clauses.append([])
            return
        total = sum(weights)
        if kind == "le" and target >= total:
            return
        if kind == "ge" and target <= 0:
            return
        if (kind == "le" and target < 0) or (kind == "ge" and target > total) \
                or (kind == "eq" and not 0 <= target <= total):
            self.clauses.append([])
            return
        encoder = {"le": PBEnc.leq, "ge": PBEnc.geq, "eq": PBEnc.equals}[kind]
        self.clauses.extend(encoder(lits=lits, weights=weights, bound=target,
                                    vpool=self.pool).clauses)

    def linear_le(self, terms, bound):
        """`sum(coefficient * var) <= bound` over `(coefficient, IntVar)` pairs."""
        self._pb(terms, bound, "le")

    def linear_ge(self, terms, bound):
        self._pb(terms, bound, "ge")

    def linear_eq(self, terms, bound):
        self._pb(terms, bound, "eq")

    def sum_eq(self, vars, bound):
        """`sum(vars) == bound`."""
        self.linear_eq([(1, v) for v in vars], bound)

    def sum_le(self, vars, bound):
        self.linear_le([(1, v) for v in vars], bound)

    def sum_ge(self, vars, bound):
        self.linear_ge([(1, v) for v in vars], bound)

    def weighted_sum_eq(self, coefficients, vars, bound):
        """`sum(coefficients[i] * vars[i]) == bound`."""
        self._require_same_length(coefficients, vars, "weighted_sum_eq")
        self.linear_eq(list(zip(coefficients, vars)), bound)

    def weighted_sum_le(self, coefficients, vars, bound):
        self._require_same_length(coefficients, vars, "weighted_sum_le")
        self.linear_le(list(zip(coefficients, vars)), bound)

    def weighted_sum_ge(self, coefficients, vars, bound):
        self._require_same_length(coefficients, vars, "weighted_sum_ge")
        self.linear_ge(list(zip(coefficients, vars)), bound)

    # --- pseudo-Boolean over plain literals -------------------------------

    def bool_sum_le(self, weights, lits, bound):
        """`sum(weights[i] * lits[i]) <= bound`, treating each literal as 0/1."""
        self._bool_pb(weights, lits, bound, "le")

    def bool_sum_ge(self, weights, lits, bound):
        self._bool_pb(weights, lits, bound, "ge")

    def bool_sum_eq(self, weights, lits, bound):
        self._bool_pb(weights, lits, bound, "eq")

    def _bool_pb(self, weights, lits, bound, kind):
        self._require_same_length(weights, lits, "a weighted Boolean sum")
        # A negative weight is the same constraint with the literal flipped and
        # the bound moved, which is how the encoders want to see it.
        kept_lits, kept_weights, offset = [], [], 0
        for weight, lit in zip(weights, lits):
            if weight == 0:
                continue
            if weight < 0:
                kept_lits.append(-lit)
                kept_weights.append(-weight)
                offset += weight
            else:
                kept_lits.append(lit)
                kept_weights.append(weight)
        target = bound - offset
        if not kept_lits:
            holds = {"le": 0 <= target, "ge": 0 >= target, "eq": target == 0}[kind]
            if not holds:
                self.clauses.append([])
            return
        total = sum(kept_weights)
        if kind == "le" and target >= total:
            return
        if kind == "ge" and target <= 0:
            return
        if (kind == "le" and target < 0) or (kind == "ge" and target > total) \
                or (kind == "eq" and not 0 <= target <= total):
            self.clauses.append([])
            return
        encoder = {"le": PBEnc.leq, "ge": PBEnc.geq, "eq": PBEnc.equals}[kind]
        self.clauses.extend(encoder(lits=kept_lits, weights=kept_weights,
                                    bound=target, vpool=self.pool).clauses)

    # --- relations between integer variables ------------------------------

    def is_value(self, var, value):
        """The literal for `var == value`, or a fixed-false literal if impossible."""
        lit = var.literal(value)
        return self.never() if lit is None else lit

    def same(self, left, right):
        """`left == right` for two integer variables."""
        for value, lit in zip(left.values, left.lits):
            other = right.literal(value)
            self.clauses.append([-lit] if other is None else [-lit, other])
        for value, lit in zip(right.values, right.lits):
            if left.literal(value) is None:
                self.clauses.append([-lit])

    def different(self, left, right):
        """`left != right` for two integer variables."""
        for value, lit in zip(left.values, left.lits):
            other = right.literal(value)
            if other is not None:
                self.clauses.append([-lit, -other])

    def all_different(self, vars):
        """Every variable takes a different value, value by value."""
        seen = []
        for var in vars:
            for value in var.values:
                if value not in seen:
                    seen.append(value)
        for value in seen:
            holders = [v.literal(value) for v in vars]
            self.at_most([lit for lit in holders if lit is not None], 1)

    def _require_same_length(self, left, right, what):
        if len(left) != len(right):
            raise ValueError(f"{what}: {len(left)} coefficients for {len(right)} terms")
