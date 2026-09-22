// Split the cows so each son gets his quota and the same total milk.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let num_cows = inst.size("num_cows");
    let num_sons = inst.size("num_sons");
    let quota = inst.ints("cows_per_son");

    // Cow i (1-based) yields i litres.
    let milk: Vec<i32> = (1..=num_cows as i32).collect();
    let total: i32 = milk.iter().sum();
    let share = total / num_sons as i32;

    let assignment: Vec<Var> = (0..num_cows)
        .map(|_| solver.new_bounded_integer(0, num_sons as i32 - 1))
        .collect();
    let target = solver.new_bounded_integer(share, share);
    for son in 0..num_sons {
        let mut mine: Vec<Lit> = Vec::new();
        for i in 0..num_cows {
            let flag = solver.new_literal();
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![assignment[i].scaled(1)], son as i32, tag))
                .reify(flag);
            mine.push(flag);
        }
        let quota_var = solver.new_bounded_integer(quota[son], quota[son]);
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_equals(
                vec![1; num_cows], mine.clone(), quota_var, tag))
            .post();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_equals(
                milk.clone(), mine, target, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("cow_assignments", assignment);
    m
}
