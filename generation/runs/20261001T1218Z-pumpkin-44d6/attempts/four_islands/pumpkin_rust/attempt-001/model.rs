// Four islands: four islands A (NW), B (NE), C (SW), D (SE) joined by bridges
// A-B, C-D (east-west) and A-C, B-D (north-south). Find each island's name,
// export and tourist attraction from six clues. Each output gives the map
// position (A=0, B=1, C=2, D=3) of a name, export or attraction.
//
// The instance has no fields: the map and the clues are the puzzle's own data,
// mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 4;
    let (a, b, c, d) = (0, 1, 2, 3);
    let island: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n - 1)).collect();
    let export: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n - 1)).collect();
    let attraction: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n - 1)).collect();
    let (pwana, quero, rayou, skern) = (island[0], island[1], island[2], island[3]);
    let (alabaster, bananas, _coconuts, durian_fruit) = (export[0], export[1], export[2], export[3]);
    let (resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve) =
        (attraction[0], attraction[1], attraction[2], attraction[3]);

    // Each island has a different name, export and attraction.
    let tag = solver.new_constraint_tag();
    for group in [&island, &export, &attraction] {
        solver.add_constraint(pumpkin_solver::all_different(group.clone(), tag)).post();
    }

    // Each clue relates the positions of two items; the allowed position pairs
    // are listed as a table.
    let clues = solver.new_constraint_tag();
    let clue = |solver: &mut Solver, first: Var, second: Var, pairs: Vec<Vec<i32>>| {
        solver.add_constraint(pumpkin_solver::table(vec![first, second], pairs, clues)).post();
    };
    // 1. The koala preserve is due south of Pwana.
    clue(solver, pwana, koala_preserve, vec![vec![a, c], vec![b, d]]);
    // 2. The alabaster island is due west of Quero.
    clue(solver, alabaster, quero, vec![vec![a, b], vec![c, d]]);
    // 3. The resort hotel is due east of the durian fruit island.
    clue(solver, durian_fruit, resort_hotel, vec![vec![a, b], vec![c, d]]);
    // 4. Skern and the jai alai stadium are joined by a north-south bridge.
    clue(solver, skern, jai_alai_stadium, vec![vec![a, c], vec![c, a], vec![b, d], vec![d, b]]);
    // 5. Rayou and the banana island are joined by an east-west bridge.
    clue(solver, rayou, bananas, vec![vec![a, b], vec![b, a], vec![c, d], vec![d, c]]);
    // 6. The ice skating rink and the jai alai stadium are not joined by a
    //    bridge: they are on opposite corners.
    clue(solver, ice_skating_rink, jai_alai_stadium, vec![vec![a, d], vec![d, a], vec![b, c], vec![c, b]]);

    let mut m = Model::new();
    m.put("island", island);
    m.put("export", export);
    m.put("attraction", attraction);
    m
}
