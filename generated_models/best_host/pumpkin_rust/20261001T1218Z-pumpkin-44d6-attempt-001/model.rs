// Best host: seat six guests around a round table so that every guest sits only
// next to the two people they get along with. x[i] is the guest in seat i.
//
// The instance has no fields: the six guests and who each one will sit next to
// are the puzzle's own data, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    // Guests: 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank.
    // prefs[g] lists the only guests g will sit next to.
    let prefs: Vec<[i32; 2]> = vec![
        [3, 5], // Andrew: Dave and Frank
        [2, 4], // Betty: Cara and Erica
        [1, 5], // Cara: Betty and Frank
        [0, 4], // Dave: Andrew and Erica
        [1, 3], // Erica: Betty and Dave
        [0, 2], // Frank: Andrew and Cara
    ];
    let n = prefs.len();

    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n as i32 - 1)).collect();

    // Every guest has exactly one seat.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();

    // The guest on each side of seat i is one that the guest in seat i will sit
    // next to. The allowed (guest, neighbour) pairs are listed as a table.
    let liked: Vec<Vec<i32>> = (0..n)
        .flat_map(|g| prefs[g].iter().map(move |&h| vec![g as i32, h]))
        .collect();
    let neighbours = solver.new_constraint_tag();
    for i in 0..n {
        let left = x[(i + n - 1) % n];
        let right = x[(i + 1) % n];
        solver.add_constraint(pumpkin_solver::table(vec![x[i], left], liked.clone(), neighbours)).post();
        solver.add_constraint(pumpkin_solver::table(vec![x[i], right], liked.clone(), neighbours)).post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
