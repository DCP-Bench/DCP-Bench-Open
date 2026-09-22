// Recover individual bale weights from every pairwise total.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let weights = inst.ints("weights");

    // 0..50 is the bound the reference declares for the puzzle.
    let bales: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, 50)).collect();
    for &w in &weights {
        let i = solver.new_bounded_integer(0, n as i32 - 1);
        let j = solver.new_bounded_integer(0, n as i32 - 1);
        // i < j, written as i - j <= -1: Pumpkin has only the upper bound form.
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![i.scaled(1), j.scaled(-1)], -1, tag))
            .post();

        let left = solver.new_bounded_integer(0, 50);
        let right = solver.new_bounded_integer(0, 50);
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::element(
                i.scaled(1), bales.clone(), left.scaled(1), tag))
            .post();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::element(
                j.scaled(1), bales.clone(), right.scaled(1), tag))
            .post();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![left.scaled(1), right.scaled(1)], w, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("bales", bales);
    m
}
