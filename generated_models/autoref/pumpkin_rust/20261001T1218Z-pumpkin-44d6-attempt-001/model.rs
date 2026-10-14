// Autoref: find a series s[0..n+1] in which each i from 0 to n occurs exactly s[i]
// times, and whose last element s[n+1] equals m.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let m_last = inst.int("m"); // value of the last element s[n+1]
    let length = n + 2;

    // s[k] is the k-th element of the series; its values range from 0 to n, as
    // in the reference.
    let s: Vec<Var> = (0..length).map(|_| solver.new_bounded_integer(0, n as i32)).collect();

    // The last element is m.
    let last = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(vec![s[n + 1].scaled(1)], m_last, last))
        .post();

    // For each i from 0 to n, i occurs s[i] times in the whole series (all n + 2
    // elements). Pumpkin has no count constraint, so for each i a literal per
    // element says "this element equals i" and the literals are summed into s[i].
    let holds = solver.new_constraint_tag();
    let occurrences = solver.new_constraint_tag();
    for i in 0..=n {
        let mut is_i: Vec<Lit> = Vec::new();
        for k in 0..length {
            let flag = solver.new_literal();
            solver
                .add_constraint(pumpkin_solver::equals(vec![s[k].scaled(1)], i as i32, holds))
                .reify(flag);
            is_i.push(flag);
        }
        solver
            .add_constraint(pumpkin_solver::boolean_equals(vec![1; length], is_i, s[i], occurrences))
            .post();
    }

    let mut m = Model::new();
    m.put("s", s);
    m
}
