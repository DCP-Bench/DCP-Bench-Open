// Largest set of mutually adjacent vertices.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let adj = inst.matrix("adj");

    let chosen: Vec<Lit> = (0..n).map(|_| solver.new_literal()).collect();
    for i in 0..n {
        for j in (i + 1)..n {
            if adj[i][j] == 0 {
                let tag = solver.new_constraint_tag();
                solver
                    .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                        vec![1, 1], vec![chosen[i], chosen[j]], 1, tag))
                    .post();
            }
        }
    }

    let size = solver.new_bounded_integer(0, n as i32);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(
            vec![1; n], chosen.clone(), size, tag))
        .post();

    let mut m = Model::new();
    m.put("c", chosen);
    m.maximise(size);
    m
}
