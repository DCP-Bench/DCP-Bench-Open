// Coins: choose how many coins of each denomination to carry, as few in total as
// possible, so that every amount from 1 up to just below the maximum can be paid
// exactly with a subset of the coins carried.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let denominations = inst.ints("denominations"); // coin values, in cents
    let max_amount = inst.int("max_amount_to_pay"); // amounts 1 .. max_amount - 1 must be payable
    let n = denominations.len();

    // x[i] is the number of coins of denomination i carried; the bounds are the reference's.
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, max_amount)).collect();
    // num_coins is the total number of coins carried, the quantity to minimise.
    let num_coins = solver.new_bounded_integer(0, max_amount);

    // num_coins = sum(x), posted as sum(x) - num_coins = 0.
    let mut terms: Vec<Term> = x.iter().map(|v| v.scaled(1)).collect();
    terms.push(num_coins.scaled(-1));
    let count = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, count))
        .post();

    // Every amount j from 1 to max_amount - 1 can be paid: for each j there are
    // payment[i] coins of denomination i, at most the x[i] carried, worth j in
    // total. A zero denomination would be a zero coefficient, which Pumpkin cannot
    // take, so coins of value 0 are left out of the sum.
    let pays = solver.new_constraint_tag();
    let available = solver.new_constraint_tag();
    for j in 1..max_amount {
        let payment: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, max_amount)).collect();
        let mut worth: Vec<Term> = payment
            .iter()
            .zip(&denominations)
            .filter(|(_, &value)| value != 0)
            .map(|(&p, &value)| p.scaled(value))
            .collect();
        if worth.is_empty() {
            worth.push(solver.new_bounded_integer(0, 0).scaled(1));
        }
        solver
            .add_constraint(pumpkin_solver::equals(worth, j, pays))
            .post();
        for i in 0..n {
            // payment[i] <= x[i]
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![payment[i].scaled(1), x[i].scaled(-1)], 0, available))
                .post();
        }
    }

    let mut m = Model::new();
    m.put("x", x);
    m.minimise(num_coins);
    m
}
