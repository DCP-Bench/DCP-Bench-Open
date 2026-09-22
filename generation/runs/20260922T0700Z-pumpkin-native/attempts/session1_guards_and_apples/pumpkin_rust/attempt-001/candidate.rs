// Each guard takes half the apples plus one; one apple survives the last gate.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let gates = inst.size("num_gates");

    // 0..100 is the bound the reference declares for the puzzle.
    let apples: Vec<Var> = (0..gates + 1).map(|_| solver.new_bounded_integer(0, 100)).collect();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(vec![apples[gates].scaled(1)], 1, tag))
        .post();
    for i in 1..=gates {
        // before == 2 * (after + 1)
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![apples[i - 1].scaled(1), apples[i].scaled(-2)], 2, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("apples", apples);
    m
}
