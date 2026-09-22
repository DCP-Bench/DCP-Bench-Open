// Put balls 1..n into c boxes so no triple x + y = z shares a box.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let c_boxes = inst.int("c");

    let balls: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, c_boxes)).collect();
    for x in 1..n {
        for y in 1..(n - x + 1) {
            let z = x + y;
            if z <= n {
                // At least one of the three pairs differs.
                let mut same: Vec<Lit> = Vec::new();
                for (left, right) in [(x - 1, y - 1), (x - 1, z - 1), (y - 1, z - 1)] {
                    let flag = solver.new_literal();
                    let tag = solver.new_constraint_tag();
                    solver
                        .add_constraint(pumpkin_solver::equals(
                            vec![balls[left].scaled(1), balls[right].scaled(-1)], 0, tag))
                        .reify(flag);
                    same.push(flag);
                }
                let differs: Vec<Lit> = same.iter().map(|&f| !f).collect();
                let tag = solver.new_constraint_tag();
                solver.add_constraint(pumpkin_solver::clause(differs, tag)).post();
            }
        }
    }

    let mut m = Model::new();
    m.put("balls", balls);
    m
}
