// Mario: plan a route from Mario's house to Luigi's house through some of the
// other houses, using at most the fuel available, so that the gold collected in
// the houses visited is as large as possible. s[i] is the house after house i on
// the route, s[i] = i for a house not on the route, and Luigi's house is followed
// by Mario's house, closing the route into one cycle.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("nHouses");
    let mario = inst.size("marioHouse");
    let luigi = inst.size("luigiHouse");
    let fuel_limit = inst.int("fuelLimit");
    let arc_fuel = inst.matrix("arc_fuel"); // arc_fuel[i][j]: fuel to go from i to j
    let gold = inst.ints("goldInHouse");

    // next[i][j] is true when house j follows house i (j == i: i is not visited).
    let next: Vec<Vec<Lit>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_literal()).collect())
        .collect();

    // Every house has exactly one successor and is the successor of exactly one
    // house, so the successors form a permutation (the reference's AllDifferent(s)).
    let permutation = solver.new_constraint_tag();
    for i in 0..n {
        let row = next[i].clone();
        let col: Vec<Lit> = (0..n).map(|k| next[k][i]).collect();
        for lits in [row, col] {
            solver.add_constraint(pumpkin_solver::clause(lits.clone(), permutation)).post();
            solver
                .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                    vec![1; n], lits, 1, permutation))
                .post();
        }
    }

    // s[i] is the number of the house following i: the sum of j * next[i][j]
    // (house 0 has weight 0 and is left out of the sum).
    let s: Vec<Var> = (0..n)
        .map(|_| solver.new_bounded_integer(0, n as i32 - 1))
        .collect();
    let successor = solver.new_constraint_tag();
    for i in 0..n {
        if n > 1 {
            let weights: Vec<i32> = (1..n as i32).collect();
            let lits: Vec<Lit> = (1..n).map(|j| next[i][j]).collect();
            solver
                .add_constraint(pumpkin_solver::boolean_equals(weights, lits, s[i], successor))
                .post();
        } else {
            solver
                .add_constraint(pumpkin_solver::equals(vec![s[i].scaled(1)], 0, successor))
                .post();
        }
    }

    // order[i] is the rank of house i on the route; ranks are all different and
    // the route starts at Mario's house with rank 1.
    let order: Vec<Var> = (0..n)
        .map(|_| solver.new_bounded_integer(1, n as i32))
        .collect();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(order.clone(), tag)).post();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(vec![order[mario].scaled(1)], 1, tag))
        .post();

    // The route ends at Luigi's house, which goes back to Mario's house.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::conjunction(vec![next[luigi][mario]], tag))
        .post();

    // Along the route the rank goes up by one from a house to its successor,
    // except on the closing step back to Mario's house. This rules out any cycle
    // that does not pass through Mario's house.
    let progression = solver.new_constraint_tag();
    for i in 0..n {
        for j in 0..n {
            if j != i && j != mario {
                solver
                    .add_constraint(pumpkin_solver::equals(
                        vec![order[j].scaled(1), order[i].scaled(-1)], 1, progression))
                    .implied_by(next[i][j]);
            }
        }
    }

    // A house not on the route ranks after Luigi's house, the last house on it:
    // order[luigi] - order[i] <= -1 whenever i is its own successor.
    let segregation = solver.new_constraint_tag();
    for i in 0..n {
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![order[luigi].scaled(1), order[i].scaled(-1)], -1, segregation))
            .implied_by(next[i][i]);
    }

    // The fuel used on the arcs travelled is within the limit. Arcs costing no
    // fuel (including staying put) are left out, since Pumpkin cannot take a
    // zero weight.
    let mut fuel_weights: Vec<i32> = Vec::new();
    let mut fuel_lits: Vec<Lit> = Vec::new();
    for i in 0..n {
        for j in 0..n {
            if arc_fuel[i][j] != 0 {
                fuel_weights.push(arc_fuel[i][j]);
                fuel_lits.push(next[i][j]);
            }
        }
    }
    let fuel = solver.new_constraint_tag();
    if !fuel_lits.is_empty() {
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                fuel_weights, fuel_lits, fuel_limit, fuel))
            .post();
    }

    // The gold collected is the gold of every house on the route (a house is on
    // the route when it is not its own successor). Houses without gold are left
    // out of the sum; the bound is all the gold there is.
    let all_gold: i32 = gold.iter().sum();
    let collected = solver.new_bounded_integer(0, all_gold.max(0));
    let mut gold_weights: Vec<i32> = Vec::new();
    let mut gold_lits: Vec<Lit> = Vec::new();
    for i in 0..n {
        if gold[i] != 0 {
            gold_weights.push(gold[i]);
            gold_lits.push(!next[i][i]);
        }
    }
    let earned = solver.new_constraint_tag();
    if gold_lits.is_empty() {
        solver
            .add_constraint(pumpkin_solver::equals(vec![collected.scaled(1)], 0, earned))
            .post();
    } else {
        solver
            .add_constraint(pumpkin_solver::boolean_equals(gold_weights, gold_lits, collected, earned))
            .post();
    }

    let mut m = Model::new();
    m.put("s", s);
    m.maximise(collected);
    m
}
