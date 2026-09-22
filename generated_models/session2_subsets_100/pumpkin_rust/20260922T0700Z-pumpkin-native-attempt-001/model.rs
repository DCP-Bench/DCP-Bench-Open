// Two disjoint non-empty subsets of A with equal sums.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let a = inst.ints("A");
    let n = a.len();

    let in_s: Vec<Lit> = (0..n).map(|_| solver.new_literal()).collect();
    let in_t: Vec<Lit> = (0..n).map(|_| solver.new_literal()).collect();

    // sum(A[i] * in_S[i]) - sum(A[i] * in_T[i]) == 0. A zero-valued element
    // contributes to neither side and cannot be scaled by zero.
    let mut balance: Vec<Term> = Vec::new();
    for i in 0..n {
        if a[i] == 0 {
            continue;
        }
        balance.push(in_s[i].get_integer_variable().scaled(a[i]));
        balance.push(in_t[i].get_integer_variable().scaled(-a[i]));
    }
    let tag = solver.new_constraint_tag();
    if balance.is_empty() {
        let zero = solver.new_bounded_integer(0, 0);
        solver
            .add_constraint(pumpkin_solver::equals(vec![zero.scaled(1)], 0, tag))
            .post();
    } else {
        solver.add_constraint(pumpkin_solver::equals(balance, 0, tag)).post();
    }

    // disjoint: no element in both
    for i in 0..n {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                vec![1, 1], vec![in_s[i], in_t[i]], 1, tag))
            .post();
    }
    // At least one each, as "at most n - 1 of the negations are true".
    for group in [&in_s, &in_t] {
        let negated: Vec<Lit> = group.iter().map(|&l| !l).collect();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                vec![1; n], negated, n as i32 - 1, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("in_S", in_s);
    m.put("in_T", in_t);
    m
}
