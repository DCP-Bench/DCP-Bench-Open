// Steiner triple system (CSPLib 44): choose n(n-1)/6 sets of three items out of
// n items such that any two sets share at most one item.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let n_sets = n * (n - 1) / 6;

    // sets[i][j] is true when item j is in set i.
    let sets: Vec<Vec<Lit>> = (0..n_sets)
        .map(|_| (0..n).map(|_| solver.new_literal()).collect())
        .collect();

    // Every set has exactly three items.
    let three = solver.new_bounded_integer(3, 3);
    let size = solver.new_constraint_tag();
    for s in &sets {
        solver
            .add_constraint(pumpkin_solver::boolean_equals(vec![1; n], s.clone(), three, size))
            .post();
    }

    // Two sets share at most one item. shared[j] is forced true when item j is in
    // both sets; forcing it only upwards suffices for an upper bound on the count.
    let intersection = solver.new_constraint_tag();
    for a in 0..n_sets {
        for b in (a + 1)..n_sets {
            let mut shared: Vec<Lit> = Vec::new();
            for j in 0..n {
                let both = solver.new_literal();
                solver
                    .add_constraint(pumpkin_solver::clause(
                        vec![!sets[a][j], !sets[b][j], both], intersection))
                    .post();
                shared.push(both);
            }
            solver
                .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                    vec![1; n], shared, 1, intersection))
                .post();
        }
    }

    // Implied constraint, added to help the search: the n(n-1)/6 sets of three
    // cover 3 pairs each, n(n-1)/2 pairs in all, and no pair twice, so every pair
    // of items is covered exactly once and each item, paired with the n-1 others
    // two at a time, lies in exactly (n-1)/2 sets.
    if n > 1 {
        let per_item = solver.new_bounded_integer(((n - 1) / 2) as i32, ((n - 1) / 2) as i32);
        let occurrences = solver.new_constraint_tag();
        for j in 0..n {
            let column: Vec<Lit> = (0..n_sets).map(|i| sets[i][j]).collect();
            if column.is_empty() {
                continue;
            }
            solver
                .add_constraint(pumpkin_solver::boolean_equals(
                    vec![1; n_sets], column, per_item, occurrences))
                .post();
        }
    }

    let mut m = Model::new();
    m.put("sets", sets);
    m
}
