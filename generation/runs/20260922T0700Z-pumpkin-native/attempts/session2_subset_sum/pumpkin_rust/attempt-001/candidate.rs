// How many bags of each coin type were stolen, given the total coins lost.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let coin_numbers = inst.ints("coin_numbers");
    let total = inst.int("total_coins_lost");
    let n = coin_numbers.len();

    let bags: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, total)).collect();
    // A bag type holding no coins contributes nothing and cannot be scaled by
    // zero, so it is dropped from the sum.
    let stolen: Vec<Term> = (0..n)
        .filter(|&i| coin_numbers[i] != 0)
        .map(|i| bags[i].scaled(coin_numbers[i]))
        .collect();
    let tag = solver.new_constraint_tag();
    if stolen.is_empty() {
        let zero = solver.new_bounded_integer(0, 0);
        solver
            .add_constraint(pumpkin_solver::equals(vec![zero.scaled(1)], total, tag))
            .post();
    } else {
        solver.add_constraint(pumpkin_solver::equals(stolen, total, tag)).post();
    }

    let mut m = Model::new();
    m.put("bags", bags);
    m
}
