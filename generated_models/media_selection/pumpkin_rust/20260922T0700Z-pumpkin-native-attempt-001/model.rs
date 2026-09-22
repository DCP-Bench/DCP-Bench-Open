// Cheapest set of media that still reaches every audience.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let incidence = inst.matrix("incidence_matrix");
    let costs = inst.ints("media_costs");
    let audiences = inst.len("target_audiences");
    let media = inst.len("advertising_media");

    let selected: Vec<Lit> = (0..media).map(|_| solver.new_literal()).collect();
    for tgt in 0..audiences {
        // At least one covering medium is chosen. A medium that does not cover
        // this audience carries coefficient zero and is dropped; the lower
        // bound is written as an upper bound on the negated terms.
        let covers: Vec<Term> = (0..media)
            .filter(|&k| incidence[tgt][k] != 0)
            .map(|k| selected[k].get_integer_variable().scaled(-incidence[tgt][k]))
            .collect();
        let tag = solver.new_constraint_tag();
        if covers.is_empty() {
            let zero = solver.new_bounded_integer(0, 0);
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![zero.scaled(1)], -1, tag))
                .post();
        } else {
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(covers, -1, tag))
                .post();
        }
    }

    let ceiling: i32 = costs.iter().sum();
    let spend = solver.new_bounded_integer(0, ceiling);
    let (prices, bought): (Vec<i32>, Vec<Lit>) = costs
        .iter()
        .zip(&selected)
        .filter(|(&w, _)| w != 0)
        .map(|(&w, &l)| (w, l))
        .unzip();
    let tag = solver.new_constraint_tag();
    if bought.is_empty() {
        solver
            .add_constraint(pumpkin_solver::equals(vec![spend.scaled(1)], 0, tag))
            .post();
    } else {
        solver
            .add_constraint(pumpkin_solver::boolean_equals(prices, bought, spend, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("is_selected", selected);
    m.put("min_total_cost", spend);
    m.minimise(spend);
    m
}
