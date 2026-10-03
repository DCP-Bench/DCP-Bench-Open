// Age changing: applying the four operations +2, /8, -3 and *7 to my age in some
// order gives my husband's age, and applying them to his age in a different
// order gives mine. Find both ages.
//
// The instance has no fields: the operations, the age range 16..120 and the
// range 1..1000 of intermediate values are the puzzle's own constants, mirrored
// from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let steps = 4;
    let (age_low, age_high) = (16, 120);

    let m_age = solver.new_bounded_integer(age_low, age_high); // my age
    let h_age = solver.new_bounded_integer(age_low, age_high); // husband's age

    // perm1[i] (perm2[i]) is the operation applied at step i when starting from my
    // (his) age: 0 is +2, 1 is /8, 2 is -3, 3 is *7. Each order uses every
    // operation once.
    let perm1: Vec<Var> = (0..steps).map(|_| solver.new_bounded_integer(0, 3)).collect();
    let perm2: Vec<Var> = (0..steps).map(|_| solver.new_bounded_integer(0, 3)).collect();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(perm1.clone(), tag)).post();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(perm2.clone(), tag)).post();

    // The two orders differ in at least one position.
    let different_order = solver.new_constraint_tag();
    let differs: Vec<Lit> = (0..steps)
        .map(|i| {
            let d = solver.new_literal();
            solver
                .add_constraint(pumpkin_solver::not_equals(
                    vec![perm1[i].scaled(1), perm2[i].scaled(-1)], 0, different_order))
                .reify(d);
            d
        })
        .collect();
    solver.add_constraint(pumpkin_solver::clause(differs, different_order)).post();

    // hlist runs from my age to his, mlist from his age to mine.
    let hlist: Vec<Var> = (0..=steps).map(|_| solver.new_bounded_integer(1, 1000)).collect();
    let mlist: Vec<Var> = (0..=steps).map(|_| solver.new_bounded_integer(1, 1000)).collect();
    let ends = solver.new_constraint_tag();
    for (a, b) in [(hlist[0], m_age), (hlist[steps], h_age), (mlist[0], h_age), (mlist[steps], m_age)] {
        solver
            .add_constraint(pumpkin_solver::equals(vec![a.scaled(1), b.scaled(-1)], 0, ends))
            .post();
    }

    // Each step applies the chosen operation: whenever op_k is chosen,
    // new == old + 2, 8 * new == old (an exact division by 8), new == old - 3,
    // or new == 7 * old, each written as a linear equation.
    let operation = solver.new_constraint_tag();
    for (perm, list) in [(&perm1, &hlist), (&perm2, &mlist)] {
        for i in 0..steps {
            let (old, new) = (list[i], list[i + 1]);
            let forms: [(Vec<Term>, i32); 4] = [
                (vec![new.scaled(1), old.scaled(-1)], 2),
                (vec![new.scaled(8), old.scaled(-1)], 0),
                (vec![new.scaled(1), old.scaled(-1)], -3),
                (vec![new.scaled(1), old.scaled(-7)], 0),
            ];
            for (k, (terms, rhs)) in forms.into_iter().enumerate() {
                let chosen = solver.new_literal();
                solver
                    .add_constraint(pumpkin_solver::equals(vec![perm[i].scaled(1)], k as i32, operation))
                    .reify(chosen);
                solver
                    .add_constraint(pumpkin_solver::equals(terms, rhs, operation))
                    .implied_by(chosen);
            }
        }
    }

    let mut out = Model::new();
    out.put("m", m_age);
    out.put("h", h_age);
    out
}
