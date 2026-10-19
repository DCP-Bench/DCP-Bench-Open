# CPMpy 1.0.0: constraint and function catalogue

Checked against the installed `cpmpy` 1.0.0: every name below resolves in the `cpmpy`
namespace. Full signatures: [global constraints](https://cpmpy.readthedocs.io/en/latest/api/expressions/globalconstraints.html),
[global functions](https://cpmpy.readthedocs.io/en/latest/api/expressions/globalfunctions.html).

## Global constraints

| Constraint | Meaning |
|---|---|
| `cp.AllDifferent(*args)` | all arguments take different values |
| `cp.AllDifferentExcept0(*args)` | all nonzero arguments differ |
| `cp.AllDifferentExceptN(args, n)` | all arguments not equal to a value in `n` differ |
| `cp.AllEqual(*args)` | all arguments take the same value |
| `cp.AllEqualExceptN(args, n)` | all arguments not equal to a value in `n` are equal |
| `cp.Circuit(*args)` | the successor array forms one Hamiltonian circuit |
| `cp.Inverse(array1, array2)` | channelling: `array1[i]` is the index of `i` in `array2` |
| `cp.Table(array, table)` | the assignment matches a row of `table` |
| `cp.ShortTable(array, table)` | as `Table`, with wildcards allowed in `table` |
| `cp.NegativeTable(array, table)` | the assignment matches no row of `table` |
| `cp.IfThenElse(cond, if_true, if_false)` | all three are Boolean expressions |
| `cp.InDomain(expr, domain)` | non-interval domain for an expression |
| `cp.Xor(arg_list)` | exclusive or |
| `cp.Cumulative(start, duration, end=None, demand=None, capacity=None)` | resource capacity is never exceeded |
| `cp.CumulativeOptional(..., is_present=None)` | `Cumulative` with optional tasks |
| `cp.NoOverlap(start, duration, end=None)` | intervals do not overlap |
| `cp.NoOverlapOptional(..., is_present=None)` | `NoOverlap` with optional tasks |
| `cp.Precedence(vars, precedence)` | values must appear in the given order |
| `cp.GlobalCardinalityCount(vars, vals, occ)` | each `vals[i]` occurs `occ[i]` times |
| `cp.Increasing(array)` / `cp.IncreasingStrict(array)` | non-decreasing / strictly increasing |
| `cp.Decreasing(array)` / `cp.DecreasingStrict(array)` | non-increasing / strictly decreasing |
| `cp.LexLess(l1, l2)` / `cp.LexLessEq(l1, l2)` | lexicographic order between two lists |
| `cp.LexChainLess(X)` / `cp.LexChainLessEq(X)` | rows of a matrix in lexicographic order |
| `cp.Regular(array, transitions, start, accepting)` | the sequence is accepted by an automaton (the right tool for row/column pattern constraints such as nonograms) |
| `cp.MDD(array, transitions, start=None, reduce=True)` | the sequence is accepted by a decision diagram |
| `cp.DirectConstraint(name, arguments, novar=None)` | call a native solver method by its name; the name is the solver's own (OR-Tools: `"AddAllDifferent"`, CamelCase); an unknown name raises `AttributeError` |

## Global functions

| Function | Meaning |
|---|---|
| `cp.Minimum(arg_list)` / `cp.Maximum(arg_list)` | minimum / maximum of the arguments; `cp.min` / `cp.max` build the same expressions and also accept several arguments |
| `cp.Abs(expr)` | absolute value (`cp.abs` is the same) |
| `cp.Element(arr, idx)` | `arr[idx]`; prefer writing `arr[idx]` directly |
| `cp.Count(arr, val)` | how many entries of `arr` equal `val` |
| `cp.Among(arr, vals)` | how many entries of `arr` take a value in `vals` |
| `cp.NValue(arr)` / `cp.NValueExcept(arr, n)` | number of distinct values, optionally ignoring `n` |
| `cp.BoolVal(arg)` | wrap a Python or NumPy Boolean as an expression |
