// A Latin square of order m with the QG3 property (a*b)*(b*a) = a.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let order = inst.size("m");
    let top = order as i32 - 1;

    let q: Vec<Vec<Var>> = (0..order)
        .map(|_| (0..order).map(|_| solver.new_bounded_integer(0, top)).collect())
        .collect();
    for i in 0..order {
        let tag = solver.new_constraint_tag();
        solver.add_constraint(pumpkin_solver::all_different(q[i].clone(), tag)).post();
        let column: Vec<Var> = (0..order).map(|r| q[r][i]).collect();
        let tag = solver.new_constraint_tag();
        solver.add_constraint(pumpkin_solver::all_different(column, tag)).post();
    }

    // q[q[a][b]][q[b][a]] == a, over the row-major flattening of q, because
    // element indexes one array with one index.
    let flat: Vec<Var> = q.iter().flatten().copied().collect();
    for a in 0..order {
        for b in 0..order {
            let index = solver.new_bounded_integer(0, (order * order) as i32 - 1);
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![q[a][b].scaled(order as i32), q[b][a].scaled(1), index.scaled(-1)],
                    0,
                    tag,
                ))
                .post();
            let target = solver.new_bounded_integer(a as i32, a as i32);
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::element(
                    index.scaled(1), flat.clone(), target.scaled(1), tag))
                .post();
        }
    }

    let mut m = Model::new();
    m.put("quasigroup", q);
    m
}
