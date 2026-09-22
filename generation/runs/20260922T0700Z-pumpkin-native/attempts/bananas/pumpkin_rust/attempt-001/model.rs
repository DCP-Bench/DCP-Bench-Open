// Buy 100 fruits for 100 dollars, with as few bananas and apples as possible.
// The prices are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let x: Vec<Var> = (0..4).map(|_| solver.new_bounded_integer(1, 100)).collect();
    let (bananas, oranges, mangoes, apples) = (x[0], x[1], x[2], x[3]);

    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(x.clone(), 100, tag)).post();
    // 3/5 per banana, 5/7 per orange, 7/9 per mango, 9/3 per apple, all
    // multiplied through by 5*7*9 = 315 to stay integral.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![
                bananas.scaled(3 * 189),
                oranges.scaled(5 * 135),
                mangoes.scaled(7 * 105),
                apples.scaled(9 * 315),
            ],
            100 * 945,
            tag,
        ))
        .post();

    // Both run 1..100, so their total runs 2..200.
    let disliked = solver.new_bounded_integer(2, 200);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![bananas.scaled(1), apples.scaled(1), disliked.scaled(-1)], 0, tag))
        .post();

    let mut m = Model::new();
    m.put("bananas", bananas);
    m.put("oranges", oranges);
    m.put("mangoes", mangoes);
    m.put("apples", apples);
    m.minimise(disliked);
    m
}
