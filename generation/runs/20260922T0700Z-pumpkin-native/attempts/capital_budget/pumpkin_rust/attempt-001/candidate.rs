// Choose investments to maximise net present value within the budget.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let npv = inst.ints("npv");
    let cash_flow = inst.ints("cash_flow");
    let budget = inst.int("budget");

    let x: Vec<Lit> = (0..npv.len()).map(|_| solver.new_literal()).collect();
    // Pumpkin scales each literal by its weight, so zero-cost investments are
    // dropped rather than passed through as a zero scale.
    let (costs, spent): (Vec<i32>, Vec<Lit>) = cash_flow
        .iter()
        .zip(&x)
        .filter(|(&w, _)| w != 0)
        .map(|(&w, &l)| (w, l))
        .unzip();
    if !spent.is_empty() {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                costs, spent, budget, tag))
            .post();
    }

    let z = solver.new_bounded_integer(0, npv.iter().sum());
    let (values, taken): (Vec<i32>, Vec<Lit>) = npv
        .iter()
        .zip(&x)
        .filter(|(&w, _)| w != 0)
        .map(|(&w, &l)| (w, l))
        .unzip();
    let tag = solver.new_constraint_tag();
    if taken.is_empty() {
        solver
            .add_constraint(pumpkin_solver::equals(vec![z.scaled(1)], 0, tag))
            .post();
    } else {
        solver
            .add_constraint(pumpkin_solver::boolean_equals(values, taken, z, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m.put("z", z);
    m.maximise(z);
    m
}
