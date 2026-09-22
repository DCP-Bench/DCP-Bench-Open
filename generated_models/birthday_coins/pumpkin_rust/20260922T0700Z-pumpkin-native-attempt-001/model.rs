// Fifteen old British coins worth one pound five shillings and sixpence.
// The currency and the totals are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    // half-crown, shilling, sixpence, in pence
    let values = [30, 12, 6];
    let total_value = 240 + 5 * 12 + 6;
    let total_coins = 15;

    let coins: Vec<Var> = (0..values.len())
        .map(|_| solver.new_bounded_integer(0, total_coins))
        .collect();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            values.iter().zip(&coins).map(|(&w, &v)| v.scaled(w)).collect::<Vec<Term>>(),
            total_value,
            tag,
        ))
        .post();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(coins.clone(), total_coins, tag))
        .post();

    let mut m = Model::new();
    m.put("half_crowns", coins[0]);
    m
}
