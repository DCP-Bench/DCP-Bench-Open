"""The modelling surface for the exact integration. Ships inside the image.

Exact is a pseudo-Boolean solver, so unlike a plain SAT solver it takes linear
constraints with integer coefficients directly, and it takes integer variables
with bounds rather than making the modeller one-hot encode them. That makes this
layer thin: most calls pass straight through to Exact.

What it does add is channelling. Anything that is not linear -- all-different,
counting how many variables take a value, indexing an array at a variable
position -- is expressed through 0/1 indicators tied to a variable by
`sum(v * y_v) == x` with `sum(y_v) == 1`. The indicators are built once per
variable, on first use, so a model that never needs them never pays for them.
"""
import exact


class Var:
    """One Exact variable, with the bounds it was declared with."""

    def __init__(self, name, lower, upper, boolean=False):
        self.name = name
        self.lower = lower
        self.upper = upper
        # Only affects how a declared output is rendered: a variable made with
        # `Pb.bool` comes back as true/false, one made with `Pb.int(0, 1)` as
        # 0/1. The brief says which the problem declares.
        self.boolean = boolean

    def values(self):
        return range(self.lower, self.upper + 1)

    def __repr__(self):
        return f"Var({self.name}, {self.lower}..{self.upper})"


class Pb:
    """Builds the pseudo-Boolean model a submission describes."""

    def __init__(self):
        self.solver = exact.Exact()
        self.objective = None
        self._next = 0
        self._indicators = {}

    # --- variables ---------------------------------------------------------

    def _name(self, prefix):
        self._next += 1
        return f"{prefix}{self._next}"

    def int(self, lo, hi):
        """An integer variable on `[lo, hi]`."""
        if lo > hi:
            raise ValueError(f"empty domain [{lo}, {hi}]")
        name = self._name("x")
        self.solver.addVariable(name, lo, hi)
        return Var(name, lo, hi)

    def ints(self, n, lo, hi):
        return [self.int(lo, hi) for _ in range(n)]

    def int_grid(self, rows, cols, lo, hi):
        return [self.ints(cols, lo, hi) for _ in range(rows)]

    def bool(self):
        """A 0/1 variable that renders as true/false in the declared outputs."""
        name = self._name("b")
        self.solver.addVariable(name, 0, 1)
        return Var(name, 0, 1, boolean=True)

    def bools(self, n):
        return [self.bool() for _ in range(n)]

    def bool_grid(self, rows, cols):
        return [self.bools(cols) for _ in range(rows)]

    def constant(self, value):
        return self.int(value, value)

    # --- linear constraints ------------------------------------------------

    @staticmethod
    def _terms(terms):
        return [(int(coefficient), var.name) for coefficient, var in terms if coefficient]

    def le(self, terms, bound):
        """`sum(coefficient * var) <= bound`."""
        self.solver.addConstraint(self._terms(terms), False, 0, True, int(bound))

    def ge(self, terms, bound):
        self.solver.addConstraint(self._terms(terms), True, int(bound), False, 0)

    def eq(self, terms, bound):
        self.solver.addConstraint(self._terms(terms), True, int(bound), True, int(bound))

    def between(self, terms, low, high):
        """`low <= sum(coefficient * var) <= high`, in one constraint."""
        self.solver.addConstraint(self._terms(terms), True, int(low), True, int(high))

    def sum_eq(self, vars, bound):
        self.eq([(1, v) for v in vars], bound)

    def sum_le(self, vars, bound):
        self.le([(1, v) for v in vars], bound)

    def sum_ge(self, vars, bound):
        self.ge([(1, v) for v in vars], bound)

    def weighted_sum_eq(self, coefficients, vars, bound):
        self._same_length(coefficients, vars, "weighted_sum_eq")
        self.eq(list(zip(coefficients, vars)), bound)

    def weighted_sum_le(self, coefficients, vars, bound):
        self._same_length(coefficients, vars, "weighted_sum_le")
        self.le(list(zip(coefficients, vars)), bound)

    def weighted_sum_ge(self, coefficients, vars, bound):
        self._same_length(coefficients, vars, "weighted_sum_ge")
        self.ge(list(zip(coefficients, vars)), bound)

    def same(self, left, right):
        self.eq([(1, left), (-1, right)], 0)

    # --- channelling, and what it buys ------------------------------------

    def indicators(self, var):
        """0/1 variables, one per value, with `y_v` true exactly when `var == v`.

        Built once per variable and cached, because everything non-linear here
        goes through them and a model often asks more than once.
        """
        if var.name not in self._indicators:
            flags = {value: self.bool() for value in var.values()}
            self.eq([(1, flag) for flag in flags.values()], 1)
            self.eq([(value, flag) for value, flag in flags.items()] + [(-1, var)], 0)
            self._indicators[var.name] = flags
        return self._indicators[var.name]

    def is_value(self, var, value):
        """A 0/1 variable that is 1 exactly when `var == value`.

        Returns a variable fixed to 0 when the value is outside the domain.
        """
        if not var.lower <= value <= var.upper:
            return self.constant(0)
        return self.indicators(var)[value]

    def different(self, left, right):
        """`left != right`, through the indicators of both."""
        shared = set(left.values()) & set(right.values())
        for value in shared:
            self.le([(1, self.is_value(left, value)), (1, self.is_value(right, value))], 1)

    def all_different(self, vars):
        """Every variable takes a different value, value by value."""
        values = sorted({value for var in vars for value in var.values()})
        for value in values:
            holders = [self.is_value(var, value) for var in vars
                       if var.lower <= value <= var.upper]
            if len(holders) > 1:
                self.le([(1, flag) for flag in holders], 1)

    def count(self, flags, target):
        """`target` equals how many of these 0/1 variables are 1."""
        self.eq([(1, flag) for flag in flags] + [(-1, target)], 0)

    def element(self, index, array, value):
        """`array[index] == value` for a constant array, with `index` 0-based."""
        flags = self.indicators(index)
        for position, flag in flags.items():
            if 0 <= position < len(array):
                # flag -> value == array[position], through a pair of big-M bounds
                span = max(array) - min(array) + 1
                self.le([(1, value), (span, flag)], array[position] + span)
                self.ge([(1, value), (-span, flag)], array[position] - span)
            else:
                self.eq([(1, flag)], 0)

    # --- cardinality over 0/1 variables ------------------------------------

    def at_most(self, flags, bound):
        self.le([(1, flag) for flag in flags], bound)

    def at_least(self, flags, bound):
        self.ge([(1, flag) for flag in flags], bound)

    def exactly(self, flags, bound):
        self.eq([(1, flag) for flag in flags], bound)

    def any(self, flags):
        self.at_least(flags, 1)

    def negate(self, flag):
        """A 0/1 variable that is the complement of this one."""
        other = self.bool()
        self.eq([(1, flag), (1, other)], 1)
        return other

    # --- objective ---------------------------------------------------------

    def minimise(self, terms):
        """Minimise `sum(coefficient * var)`. Exact takes the expression itself."""
        self.objective = (list(terms), True)

    def maximise(self, terms):
        self.objective = (list(terms), False)

    @staticmethod
    def _same_length(left, right, what):
        if len(left) != len(right):
            raise ValueError(f"{what}: {len(left)} coefficients for {len(right)} terms")
