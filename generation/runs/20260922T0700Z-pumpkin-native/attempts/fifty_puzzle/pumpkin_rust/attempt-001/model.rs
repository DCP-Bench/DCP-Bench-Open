// Knock over the dummies whose numbers add up to exactly the target.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let values = inst.ints("values");
    let target = inst.int("target_sum");

    let dummies: Vec<Lit> = (0..values.len()).map(|_| solver.new_literal()).collect();
    // A zero-valued dummy contributes nothing and cannot be scaled by zero.
    let terms: Vec<Term> = values
        .iter()
        .zip(&dummies)
        .filter(|(&w, _)| w != 0)
        .map(|(&w, l)| l.get_integer_variable().scaled(w))
        .collect();
    let tag = solver.new_constraint_tag();
    if terms.is_empty() {
        let zero = solver.new_bounded_integer(0, 0);
        solver
            .add_constraint(pumpkin_solver::equals(vec![zero.scaled(1)], target, tag))
            .post();
    } else {
        solver.add_constraint(pumpkin_solver::equals(terms, target, tag)).post();
    }

    let mut m = Model::new();
    m.put("dummies", dummies);
    m
}
