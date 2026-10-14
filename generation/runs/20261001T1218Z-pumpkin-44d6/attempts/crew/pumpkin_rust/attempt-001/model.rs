// Crew: assign cabin crew to flights so that every flight has the required
// number of crew with the required roles and languages, and nobody works two
// flights within three consecutive ones (two flights off after a flown flight).

// `sum(weights[k] * lits[k]) >= rhs`. Pumpkin only has "<=", so the weights and
// the bound are negated; zero weights are dropped because Pumpkin cannot take a
// zero coefficient. When no term is left the sum is 0, which is posted over a
// variable fixed at 0 because Pumpkin cannot post an empty linear constraint.
fn at_least(solver: &mut Solver, weights: &[i32], lits: &[Lit], rhs: i32, tag: pumpkin_solver::core::proof::ConstraintTag) {
    let mut terms: Vec<Term> = weights
        .iter()
        .zip(lits)
        .filter(|(&w, _)| w != 0)
        .map(|(&w, l)| l.get_integer_variable().scaled(-w))
        .collect();
    if terms.is_empty() {
        terms.push(solver.new_bounded_integer(0, 0).scaled(1));
    }
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(terms, -rhs, tag))
        .post();
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    // attributes[p] = [steward, hostess, french, spanish, german] of person p (0/1 each)
    let attributes = inst.matrix("attributes");
    // required_crew[f] = [crew size, stewards, hostesses, french, spanish, german] needed on flight f
    let required_crew = inst.matrix("required_crew");
    let num_persons = attributes.len();
    let num_flights = required_crew.len();

    // crew[f][p] is true when person p is assigned to flight f.
    let crew: Vec<Vec<Lit>> = (0..num_flights)
        .map(|_| (0..num_persons).map(|_| solver.new_literal()).collect())
        .collect();

    // Each flight has exactly the required number of crew members.
    let flight_size = solver.new_constraint_tag();
    for f in 0..num_flights {
        let size = required_crew[f][0];
        let ones = vec![1; num_persons];
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(ones.clone(), crew[f].clone(), size, flight_size))
            .post();
        at_least(solver, &ones, &crew[f], size, flight_size);
    }

    // Each flight has at least the required number of stewards, hostesses and
    // speakers of French, Spanish and German among its crew.
    let skills = solver.new_constraint_tag();
    for f in 0..num_flights {
        for j in 0..5 {
            let has_skill: Vec<i32> = (0..num_persons).map(|p| attributes[p][j]).collect();
            at_least(solver, &has_skill, &crew[f], required_crew[f][j + 1], skills);
        }
    }

    // After a flight a person has two flights off: among any three consecutive
    // flights a person works at most one.
    let rest = solver.new_constraint_tag();
    for f in 0..num_flights.saturating_sub(2) {
        for p in 0..num_persons {
            let window = vec![crew[f][p], crew[f + 1][p], crew[f + 2][p]];
            solver
                .add_constraint(pumpkin_solver::boolean_less_than_or_equals(vec![1, 1, 1], window, 1, rest))
                .post();
        }
    }

    // The reference counts the persons who work at least one flight in a variable
    // that ranges from 1, so at least one person must work. That is the same as
    // some crew[f][p] being true.
    let someone_works = solver.new_constraint_tag();
    let everyone: Vec<Lit> = crew.iter().flatten().copied().collect();
    solver
        .add_constraint(pumpkin_solver::clause(everyone, someone_works))
        .post();

    let mut m = Model::new();
    m.put("crew", crew);
    m
}
