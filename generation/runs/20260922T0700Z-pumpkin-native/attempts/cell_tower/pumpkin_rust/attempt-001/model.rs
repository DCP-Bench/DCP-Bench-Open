// Build towers within budget to cover the most people.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let delta = inst.matrix("delta");
    let cost = inst.ints("cost");
    let population = inst.ints("population");
    let budget = inst.int("budget");
    let sites = cost.len();
    let regions = population.len();

    let build_tower: Vec<Lit> = (0..sites).map(|_| solver.new_literal()).collect();
    let covered: Vec<Lit> = (0..regions).map(|_| solver.new_literal()).collect();

    // A region only counts as covered if some chosen site reaches it. A site
    // that does not reach it carries coefficient zero, which Pumpkin cannot
    // scale by, so those terms are dropped.
    for j in 0..regions {
        // A Literal enters a linear constraint as the 0/1 integer view it
        // already is; scaled() on the literal itself is a different type.
        let mut row: Vec<Term> = vec![covered[j].get_integer_variable()];
        row.extend(
            (0..sites)
                .filter(|&i| delta[i][j] != 0)
                .map(|i| build_tower[i].get_integer_variable().scaled(-delta[i][j])),
        );
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(row, 0, tag))
            .post();
    }

    let (costs, built): (Vec<i32>, Vec<Lit>) = cost
        .iter()
        .zip(&build_tower)
        .filter(|(&w, _)| w != 0)
        .map(|(&w, &l)| (w, l))
        .unzip();
    if !built.is_empty() {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                costs, built, budget, tag))
            .post();
    }

    let ceiling: i32 = population.iter().sum();
    let reached = solver.new_bounded_integer(0, ceiling);
    let (people, reach): (Vec<i32>, Vec<Lit>) = population
        .iter()
        .zip(&covered)
        .filter(|(&w, _)| w != 0)
        .map(|(&w, &l)| (w, l))
        .unzip();
    let tag = solver.new_constraint_tag();
    if reach.is_empty() {
        solver
            .add_constraint(pumpkin_solver::equals(vec![reached.scaled(1)], 0, tag))
            .post();
    } else {
        solver
            .add_constraint(pumpkin_solver::boolean_equals(people, reach, reached, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("build_tower", build_tower);
    m.put("total_population_covered", reached);
    m.maximise(reached);
    m
}
