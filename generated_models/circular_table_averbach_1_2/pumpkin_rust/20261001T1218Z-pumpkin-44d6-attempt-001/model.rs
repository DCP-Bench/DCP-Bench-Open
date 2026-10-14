// Circular table (Averbach 1.2): players X, Y, Z of nationalities American,
// English and French sit round a table and each passes cards to the person on
// their right. Y passed to the American; X passed to the person who passed to the
// Frenchwoman. Seats are 0, 1, 2 with seat (s + 1) mod 3 to the right of seat s;
// a player and a nationality with the same seat are the same person.
//
// The instance has no fields: the three seats and the two clues are the puzzle's
// own constants, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 3;
    let players: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n - 1)).collect();
    let (x, y, _z) = (players[0], players[1], players[2]);
    let nationalities: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n - 1)).collect();
    let (american, _english, french) = (nationalities[0], nationalities[1], nationalities[2]);

    // Each player and each nationality occupies a different seat.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(players.clone(), tag)).post();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(nationalities.clone(), tag)).post();

    // "a sits right of b" means a == (b + 1) mod 3, listed as allowed (a, b) pairs.
    let right_of: Vec<Vec<i32>> = (0..n).map(|b| vec![(b + 1) % n, b]).collect();
    let clues = solver.new_constraint_tag();
    // Y passed three hearts to the American: the American sits right of Y.
    solver.add_constraint(pumpkin_solver::table(vec![american, y], right_of.clone(), clues)).post();
    // X passed to the person who passed to the Frenchwoman: X sits right of the
    // Frenchwoman, as in the reference.
    solver.add_constraint(pumpkin_solver::table(vec![x, french], right_of, clues)).post();

    let mut m = Model::new();
    m.put("x", players[0]);
    m.put("y", players[1]);
    m.put("z", players[2]);
    m.put("american", nationalities[0]);
    m.put("english", nationalities[1]);
    m.put("french", nationalities[2]);
    m
}
