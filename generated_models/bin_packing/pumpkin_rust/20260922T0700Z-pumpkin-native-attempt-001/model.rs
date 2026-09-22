// Assign each item to a bin without exceeding the bin capacity.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let weights = inst.ints("weights");
    let capacity = inst.int("capacity");
    let num_bins = inst.int("num_bins");
    let n = weights.len();

    let bins: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, num_bins - 1)).collect();
    for b in 0..num_bins {
        // Weight actually placed in bin b, through a reified indicator per item.
        let mut here: Vec<Lit> = Vec::new();
        for j in 0..n {
            let flag = solver.new_literal();
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::equals(vec![bins[j].scaled(1)], b, tag))
                .reify(flag);
            here.push(flag);
        }
        // A zero weight would divide by zero inside Pumpkin, so drop those.
        let (kept_weights, kept_lits): (Vec<i32>, Vec<Lit>) = weights
            .iter()
            .zip(&here)
            .filter(|(&w, _)| w != 0)
            .map(|(&w, &l)| (w, l))
            .unzip();
        if kept_lits.is_empty() {
            continue;
        }
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                kept_weights, kept_lits, capacity, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("bins", bins);
    m
}
