// Maximise the value carried without exceeding the knapsack capacity.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let values = inst.ints("values");
    let weights = inst.ints("weights");
    let capacity = inst.int("capacity");

    let x: Vec<Lit> = (0..values.len()).map(|_| solver.new_literal()).collect();
    // Pumpkin scales each literal by its weight, so a weightless item is
    // dropped rather than passed through as a zero scale.
    let (kept, packed): (Vec<i32>, Vec<Lit>) = weights
        .iter()
        .zip(&x)
        .filter(|(&w, _)| w != 0)
        .map(|(&w, &l)| (w, l))
        .unzip();
    if !packed.is_empty() {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                kept, packed, capacity, tag))
            .post();
    }

    let total: i32 = values.iter().sum();
    let profit = solver.new_bounded_integer(0, total);
    let (worth, carried): (Vec<i32>, Vec<Lit>) = values
        .iter()
        .zip(&x)
        .filter(|(&w, _)| w != 0)
        .map(|(&w, &l)| (w, l))
        .unzip();
    let tag = solver.new_constraint_tag();
    if carried.is_empty() {
        solver
            .add_constraint(pumpkin_solver::equals(vec![profit.scaled(1)], 0, tag))
            .post();
    } else {
        solver
            .add_constraint(pumpkin_solver::boolean_equals(worth, carried, profit, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m.maximise(profit);
    m
}
