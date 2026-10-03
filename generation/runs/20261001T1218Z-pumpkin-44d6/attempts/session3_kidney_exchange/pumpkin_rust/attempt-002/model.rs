// Kidney exchange: people on a waiting list can donate a kidney to the people
// they are compatible with. Anyone who gives a kidney must receive one, and
// nobody gives or receives more than one. Maximise the number of transplants.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("num_people");
    // compatible[i] lists (1-based) the people i can donate to. The lists differ
    // in length, so the field is read from the raw JSON value.
    let compatible: Vec<Vec<usize>> = inst
        .get("compatible")
        .as_array()
        .expect("compatible: expected an array of lists")
        .iter()
        .map(|row| {
            row.as_array()
                .expect("compatible[i]: expected a list")
                .iter()
                .map(|v| v.as_i64().expect("compatible entry: expected an integer") as usize - 1)
                .collect()
        })
        .collect();

    // transplants[i][j] is true when i donates to j. A pair that is not
    // compatible gets the constant false literal: that transplant cannot happen.
    let never = solver.get_false_literal();
    let transplants: Vec<Vec<Lit>> = (0..n)
        .map(|i| {
            (0..n)
                .map(|j| if compatible[i].contains(&j) { solver.new_literal() } else { never })
                .collect()
        })
        .collect();

    let gives_receives = solver.new_constraint_tag();
    let at_most_once = solver.new_constraint_tag();
    for i in 0..n {
        let gives: Vec<Lit> = transplants[i].clone();
        let receives: Vec<Lit> = (0..n).map(|k| transplants[k][i]).collect();
        // Anyone who gives a kidney must receive one: if i donates to j, some k
        // donates to i.
        for j in 0..n {
            let mut clause = vec![!gives[j]];
            clause.extend(receives.iter().copied());
            solver
                .add_constraint(pumpkin_solver::clause(clause, gives_receives))
                .post();
        }
        // Each person donates at most once and receives at most once.
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                vec![1; n], gives, 1, at_most_once))
            .post();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                vec![1; n], receives, 1, at_most_once))
            .post();
    }

    // Implied constraint, added to help prove the optimum: every person gives at
    // most as many kidneys as they receive (a giver must receive, and nobody
    // receives more than one), and summed over everyone both counts equal the
    // number of transplants, so each person gives exactly as many as they
    // receive. The transplants therefore form disjoint cycles.
    let balance = solver.new_constraint_tag();
    for i in 0..n {
        let mut terms: Vec<Term> = Vec::new();
        for k in 0..n {
            if k == i {
                continue; // a self-donation counts once each way and cancels
            }
            if compatible[i].contains(&k) {
                terms.push(transplants[i][k].get_integer_variable().scaled(1));
            }
            if compatible[k].contains(&i) {
                terms.push(transplants[k][i].get_integer_variable().scaled(-1));
            }
        }
        if !terms.is_empty() {
            solver.add_constraint(pumpkin_solver::equals(terms, 0, balance)).post();
        }
    }

    // The objective is the number of transplants.
    let count = solver.new_bounded_integer(0, (n * n) as i32);
    let all: Vec<Lit> = transplants.iter().flatten().copied().collect();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(vec![1; all.len()], all, count, tag))
        .post();

    let mut m = Model::new();
    m.put("transplants", transplants);
    m.maximise(count);
    m
}
