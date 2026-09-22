// Fewest raw rolls cut, using the given patterns to meet every order.
//
// The instance also carries `roll_width` and the `widths` themselves. The
// reference uses neither in a constraint, only `len(widths)`: the patterns in
// `num_rolls_width` already encode what fits on a roll, so re-deriving them
// here would be a different problem from the one the reference states.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let orders = inst.ints("orders");
    let num_patterns = inst.size("num_patterns");
    let per_pattern = inst.matrix("num_rolls_width");
    let widths = inst.len("widths");

    // 0..100 uses of each pattern is the bound the reference declares.
    let used: Vec<Var> = (0..num_patterns).map(|_| solver.new_bounded_integer(0, 100)).collect();
    for i in 0..widths {
        // A pattern that yields nothing of this width carries coefficient zero,
        // which Pumpkin cannot scale by, so those terms are dropped. The bound
        // is a lower one, written as an upper bound on the negated terms.
        let row: Vec<Term> = (0..num_patterns)
            .filter(|&j| per_pattern[j][i] != 0)
            .map(|j| used[j].scaled(-per_pattern[j][i]))
            .collect();
        let tag = solver.new_constraint_tag();
        if row.is_empty() {
            let zero = solver.new_bounded_integer(0, 0);
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![zero.scaled(1)], -orders[i], tag))
                .post();
        } else {
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(row, -orders[i], tag))
                .post();
        }
    }

    let rolls = solver.new_bounded_integer(0, 100 * num_patterns as i32);
    let mut total: Vec<Term> = used.iter().map(|v| v.scaled(1)).collect();
    total.push(rolls.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(total, 0, tag)).post();

    let mut m = Model::new();
    m.put("patterns_used", used);
    m.put("min_rolls_cut", rolls);
    m.minimise(rolls);
    m
}
