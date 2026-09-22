// Pick exactly m of the given integers so that they sum to zero.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let nums = inst.ints("nums");
    let wanted = inst.int("m");
    let n = nums.len();

    let indices: Vec<Lit> = (0..n).map(|_| solver.new_literal()).collect();
    // This instance's `nums` contains a zero, and Pumpkin cannot scale a
    // variable by zero: the view escapes the non-zero assertion and divides by
    // zero inside a propagator later. A zero adds nothing to the sum, so it is
    // dropped here rather than scaled.
    let picked: Vec<Term> = (0..n)
        .filter(|&k| nums[k] != 0)
        .map(|k| indices[k].get_integer_variable().scaled(nums[k]))
        .collect();
    let tag = solver.new_constraint_tag();
    if picked.is_empty() {
        let zero = solver.new_bounded_integer(0, 0);
        solver
            .add_constraint(pumpkin_solver::equals(vec![zero.scaled(1)], 0, tag))
            .post();
    } else {
        solver.add_constraint(pumpkin_solver::equals(picked, 0, tag)).post();
    }

    let target = solver.new_bounded_integer(wanted, wanted);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(
            vec![1; n], indices.clone(), target, tag))
        .post();

    let mut m = Model::new();
    m.put("indices", indices);
    m
}
