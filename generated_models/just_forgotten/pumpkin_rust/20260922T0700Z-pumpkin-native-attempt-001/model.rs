// A permutation of the digits agreeing with each guess in exactly k places.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let sets = inst.matrix("sets");
    let correct = inst.int("num_correct_digits");
    let n = sets[0].len();

    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n as i32 - 1)).collect();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();

    let target = solver.new_bounded_integer(correct, correct);
    for guess in &sets {
        let mut hits: Vec<Lit> = Vec::new();
        for i in 0..n {
            let flag = solver.new_literal();
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::equals(vec![x[i].scaled(1)], guess[i], tag))
                .reify(flag);
            hits.push(flag);
        }
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_equals(vec![1; n], hits, target, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
