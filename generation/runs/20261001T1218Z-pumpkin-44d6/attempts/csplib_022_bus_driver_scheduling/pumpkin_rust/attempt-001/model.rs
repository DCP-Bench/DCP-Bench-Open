// Bus driver scheduling: pick a set of shifts that covers every task (piece of
// work) exactly once, using as few shifts as possible.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let num_work = inst.size("num_work"); // number of tasks
    let shifts = inst.matrix("shifts"); // shifts[i] lists the tasks shift i covers
    let num_shifts = shifts.len();

    // x[i] is true when shift i is selected.
    let x: Vec<Lit> = (0..num_shifts).map(|_| solver.new_literal()).collect();

    // Each task is covered by exactly one selected shift (set partitioning).
    let partition = solver.new_constraint_tag();
    for t in 0..num_work {
        let covering_shifts: Vec<Lit> = (0..num_shifts)
            .filter(|&i| shifts[i].contains(&(t as i32)))
            .map(|i| x[i])
            .collect();
        if covering_shifts.is_empty() {
            // No shift covers this task, so the sum is 0 and cannot equal 1.
            let never = solver.get_false_literal();
            solver
                .add_constraint(pumpkin_solver::clause(vec![never], partition))
                .post();
        } else {
            let one = solver.new_bounded_integer(1, 1);
            let weights = vec![1; covering_shifts.len()];
            solver
                .add_constraint(pumpkin_solver::boolean_equals(weights, covering_shifts, one, partition))
                .post();
        }
    }

    // The objective is the number of selected shifts, between 0 and num_shifts.
    let total = solver.new_bounded_integer(0, num_shifts as i32);
    let count = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(vec![1; num_shifts], x.clone(), total, count))
        .post();

    let mut m = Model::new();
    m.put("x", x);
    m.minimise(total);
    m
}
