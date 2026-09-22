// Langford's problem: the two copies of i sit i places apart.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let k = inst.size("k");
    let length = 2 * k;

    let position: Vec<Var> = (0..length)
        .map(|_| solver.new_bounded_integer(0, length as i32 - 1))
        .collect();
    let sol: Vec<Var> = (0..length).map(|_| solver.new_bounded_integer(1, k as i32)).collect();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(position.clone(), tag)).post();

    for i in 1..=k {
        // the second copy of i is i + 1 places after the first
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![position[i + k - 1].scaled(1), position[i - 1].scaled(-1)],
                i as i32 + 1,
                tag,
            ))
            .post();
        let value = solver.new_bounded_integer(i as i32, i as i32);
        for slot in [position[i - 1], position[k + i - 1]] {
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::element(
                    slot.scaled(1), sol.clone(), value.scaled(1), tag))
                .post();
        }
    }

    let mut m = Model::new();
    m.put("sol", sol);
    m
}
