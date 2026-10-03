// Travelling salesman: visit every city exactly once and return to the start,
// travelling the shortest total distance. Distances are Euclidean distances
// between the city locations, rounded to an integer.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let locations = inst.matrix("locations");
    let n = locations.len();

    // dist[i][j]: the rounded Euclidean distance from city i to city j. A square
    // root of an integer is never exactly halfway between two integers, so
    // rounding cannot depend on the tie rule.
    let dist: Vec<Vec<i32>> = (0..n)
        .map(|i| {
            (0..n)
                .map(|j| {
                    let dx = (locations[i][0] - locations[j][0]) as f64;
                    let dy = (locations[i][1] - locations[j][1]) as f64;
                    (dx * dx + dy * dy).sqrt().round() as i32
                })
                .collect()
        })
        .collect();
    let longest = dist.iter().flatten().copied().max().unwrap_or(0);

    if n == 1 {
        // A single city: the tour stays put and travels nothing.
        let zero = solver.new_bounded_integer(0, 0);
        let mut m = Model::new();
        m.put("travel_distance", zero);
        m.minimise(zero);
        return m;
    }

    // succ[i] is the city visited right after city i, and next[i][j] is true
    // exactly when succ[i] == j.
    let succ: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n as i32 - 1)).collect();
    let pred: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n as i32 - 1)).collect();
    let next: Vec<Vec<Lit>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_literal()).collect())
        .collect();
    let channel = solver.new_constraint_tag();
    for i in 0..n {
        for j in 0..n {
            solver
                .add_constraint(pumpkin_solver::equals(vec![succ[i].scaled(1)], j as i32, channel))
                .reify(next[i][j]);
            // pred[j] is the city visited right before j: the same arc seen from j.
            solver
                .add_constraint(pumpkin_solver::equals(vec![pred[j].scaled(1)], i as i32, channel))
                .reify(next[i][j]);
        }
    }

    // The successors form one circuit through all cities (the reference's
    // Circuit): no city is its own successor, every city is entered exactly once,
    // and ranks along the tour starting from city 0 go up by one on every arc that
    // does not return to city 0, which rules out shorter cycles.
    let circuit = solver.new_constraint_tag();
    for i in 0..n {
        solver
            .add_constraint(pumpkin_solver::conjunction(vec![!next[i][i]], circuit))
            .post();
    }
    solver.add_constraint(pumpkin_solver::all_different(succ.clone(), circuit)).post();
    solver.add_constraint(pumpkin_solver::all_different(pred.clone(), circuit)).post();
    let rank: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n as i32 - 1)).collect();
    solver
        .add_constraint(pumpkin_solver::equals(vec![rank[0].scaled(1)], 0, circuit))
        .post();
    for i in 0..n {
        for j in 1..n {
            if i != j {
                solver
                    .add_constraint(pumpkin_solver::equals(
                        vec![rank[j].scaled(1), rank[i].scaled(-1)], 1, circuit))
                    .implied_by(next[i][j]);
            }
        }
    }

    // out_len[i] is the length of the arc leaving city i and in_len[i] of the arc
    // entering it, both read from the distance table at the chosen neighbour.
    let arc = solver.new_constraint_tag();
    let mut out_len: Vec<Var> = Vec::new();
    let mut in_len: Vec<Var> = Vec::new();
    for i in 0..n {
        let row: Vec<Var> = (0..n).map(|j| solver.new_bounded_integer(dist[i][j], dist[i][j])).collect();
        let col: Vec<Var> = (0..n).map(|j| solver.new_bounded_integer(dist[j][i], dist[j][i])).collect();
        let o = solver.new_bounded_integer(0, longest);
        let e = solver.new_bounded_integer(0, longest);
        solver
            .add_constraint(pumpkin_solver::element(succ[i].scaled(1), row, o.scaled(1), arc))
            .post();
        solver
            .add_constraint(pumpkin_solver::element(pred[i].scaled(1), col, e.scaled(1), arc))
            .post();
        out_len.push(o);
        in_len.push(e);
    }

    // The travel distance is the sum of the arcs travelled.
    let total_bound: i32 = longest * n as i32;
    let travel_distance = solver.new_bounded_integer(0, total_bound);
    let objective = solver.new_constraint_tag();
    let mut terms: Vec<Term> = out_len.iter().map(|v| v.scaled(1)).collect();
    terms.push(travel_distance.scaled(-1));
    solver.add_constraint(pumpkin_solver::equals(terms, 0, objective)).post();

    // Implied constraints, added to help prove the optimum (true of every tour):
    // the entering arcs also add up to the travel distance; and with three or
    // more cities a city is entered from and left to two different neighbours,
    // so its two arcs together cost dist[i][succ] + dist[pred][i] with succ != pred.
    let implied = solver.new_constraint_tag();
    let mut terms: Vec<Term> = in_len.iter().map(|v| v.scaled(1)).collect();
    terms.push(travel_distance.scaled(-1));
    solver.add_constraint(pumpkin_solver::equals(terms, 0, implied)).post();
    // touching[i] is that cost; a table over (succ[i], pred[i], touching[i])
    // lists every pair of different neighbours, so the bound follows the
    // neighbours still possible during search, not only the two nearest.
    if n >= 3 {
        let mut both: Vec<Term> = Vec::new();
        for i in 0..n {
            let mut rows: Vec<Vec<i32>> = Vec::new();
            for s in 0..n {
                for p in 0..n {
                    if s != i && p != i && s != p {
                        rows.push(vec![s as i32, p as i32, dist[i][s] + dist[p][i]]);
                    }
                }
            }
            let touching = solver.new_bounded_integer(0, 2 * longest);
            solver
                .add_constraint(pumpkin_solver::table(vec![succ[i], pred[i], touching], rows, implied))
                .post();
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![touching.scaled(1), out_len[i].scaled(-1), in_len[i].scaled(-1)], 0, implied))
                .post();
            both.push(touching.scaled(1));
        }
        // Every arc is counted once leaving and once entering.
        both.push(travel_distance.scaled(-2));
        solver.add_constraint(pumpkin_solver::equals(both, 0, implied)).post();

        // Symmetry breaking derived here (the reference has none): the distances
        // are symmetric, so a tour and the same tour driven backwards have the
        // same length. Only the length is a declared output, so keeping the
        // direction in which city 0's successor is the smaller-numbered of its
        // two neighbours removes no output value.
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![succ[0].scaled(1), pred[0].scaled(-1)], -1, implied))
            .post();
    }

    let mut m = Model::new();
    m.put("travel_distance", travel_distance);
    m.minimise(travel_distance);
    m
}
