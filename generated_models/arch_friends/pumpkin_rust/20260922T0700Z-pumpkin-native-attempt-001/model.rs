// Match four pairs of shoes to the four stops they were bought at.
// The clues are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 4;
    let shoes: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, n as i32)).collect();
    let store: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, n as i32)).collect();
    for group in [&shoes, &store] {
        let tag = solver.new_constraint_tag();
        solver.add_constraint(pumpkin_solver::all_different(group.clone(), tag)).post();
    }

    let (ecru, fuchsia, purple, suede) = (shoes[0], shoes[1], shoes[2], shoes[3]);
    let (footfarm, heels, palace, tootsies) = (store[0], store[1], store[2], store[3]);

    // 1. fuchsia flats came from Heels in a Handcart
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![fuchsia.scaled(1), heels.scaled(-1)], 0, tag))
        .post();
    // 2. the stop after the purple pumps was not Tootsies
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::not_equals(
            vec![purple.scaled(1), tootsies.scaled(-1)], -1, tag))
        .post();
    // 3. the Foot Farm was the second stop
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(vec![footfarm.scaled(1)], 2, tag))
        .post();
    // 4. the suede sandals came two stops after The Shoe Palace
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![palace.scaled(1), suede.scaled(-1)], -2, tag))
        .post();

    let mut m = Model::new();
    m.put("ecruespadrilles", ecru);
    m.put("fuchsiaflats", fuchsia);
    m.put("purplepumps", purple);
    m.put("suedesandals", suede);
    m.put("footfarm", footfarm);
    m.put("heelsinahandcart", heels);
    m.put("theshoepalace", palace);
    m.put("tootsies", tootsies);
    m
}
