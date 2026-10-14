// Football squad: buy players so that their total price comes as close as
// possible to the GBP 30 million budget without going over, with exactly one
// goalkeeper, at least two defenders, three midfielders and two strikers, and at
// least eleven players in all. z is the total price in GBP thousands.
//
// The instance has no fields: the prices, the per-position limits, the budget
// and the squad size are the puzzle's own constants, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let budget = 30000; // GBP thousands
    let min_players = 11;
    // Prices in GBP thousands, per position.
    let costs: Vec<Vec<i32>> = vec![
        vec![730, 1280, 3880],                                                  // goalkeepers
        vec![920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],                    // defenders
        vec![1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],       // midfielders
        vec![4460, 6470, 7780, 8390, 9500],                                     // strikers
    ];
    // How many of each position to buy: (at least, at most). The upper limits
    // other than the goalkeeper's are the largest group size, as in the reference.
    let largest = costs.iter().map(|c| c.len()).max().unwrap() as i32;
    let min_max = [(1, 1), (2, largest), (3, largest), (2, largest)];

    // x[p][j]: player j of position p is bought.
    let x: Vec<Vec<Lit>> = costs.iter().map(|c| c.iter().map(|_| solver.new_literal()).collect()).collect();

    // The number bought of each position lies within its limits.
    let positions = solver.new_constraint_tag();
    for (p, &(lo, hi)) in min_max.iter().enumerate() {
        let chosen = x[p].clone();
        let n = chosen.len() as i32;
        let negated: Vec<Lit> = chosen.iter().map(|&l| !l).collect();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(vec![1; chosen.len()], chosen, hi, positions))
            .post();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(vec![1; negated.len()], negated, n - lo, positions))
            .post();
    }

    // At least eleven players in total: at most (all - 11) are left out.
    let all: Vec<Lit> = x.iter().flatten().map(|&l| !l).collect();
    let total = all.len() as i32;
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_less_than_or_equals(vec![1; all.len()], all, total - min_players, tag))
        .post();

    // z is the total price, which may not exceed the budget (its upper bound).
    let z = solver.new_bounded_integer(0, budget);
    let weights: Vec<i32> = costs.iter().flatten().copied().collect();
    let bought: Vec<Lit> = x.iter().flatten().copied().collect();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::boolean_equals(weights, bought, z, tag)).post();

    let mut m = Model::new();
    m.put("z", z);
    m.maximise(z);
    m
}
