// Template design (CSPLib 2): lay out n_templates printing templates, each with
// n_slots slots filled with design variations, and decide how many sheets to
// print from each template, so that the demand for every variation is met with
// as few printed sheets as possible.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n_slots = inst.int("n_slots");
    let n_templates = inst.size("n_templates");
    let n_var = inst.size("n_var");
    let demand = inst.ints("demand");

    // As in the reference, a template is printed between 1 and max(demand) times,
    // and holds between 0 and n_var copies of each variation.
    let ub = *demand.iter().max().unwrap();
    let production: Vec<Var> = (0..n_templates)
        .map(|_| solver.new_bounded_integer(1, ub))
        .collect();
    let layout: Vec<Vec<Var>> = (0..n_templates)
        .map(|_| (0..n_var).map(|_| solver.new_bounded_integer(0, n_var as i32)).collect())
        .collect();

    // All slots of every template are filled.
    let slots = solver.new_constraint_tag();
    for t in 0..n_templates {
        solver
            .add_constraint(pumpkin_solver::equals(layout[t].clone(), n_slots, slots))
            .post();
    }

    // The demand for each variation is met: the copies printed,
    // sum over templates of production[t] * layout[t][v], are at least demand[v].
    // printed[t][v] = production[t] * layout[t][v]; the ">=" is written as
    // -sum <= -demand because Pumpkin has only "<=".
    let product = solver.new_constraint_tag();
    let meet = solver.new_constraint_tag();
    let printed: Vec<Vec<Var>> = (0..n_templates)
        .map(|t| {
            (0..n_var)
                .map(|v| {
                    let p = solver.new_bounded_integer(0, ub * n_var as i32);
                    solver
                        .add_constraint(pumpkin_solver::times(production[t], layout[t][v], p, product))
                        .post();
                    p
                })
                .collect()
        })
        .collect();
    for v in 0..n_var {
        let terms: Vec<Term> = (0..n_templates).map(|t| printed[t][v].scaled(-1)).collect();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(terms, -demand[v], meet))
            .post();
    }

    // The number of printed sheets, which is minimised.
    let sheets = solver.new_bounded_integer(n_templates as i32, ub * n_templates as i32);
    let tag = solver.new_constraint_tag();
    let mut terms: Vec<Term> = production.iter().map(|p| p.scaled(1)).collect();
    terms.push(sheets.scaled(-1));
    solver.add_constraint(pumpkin_solver::equals(terms, 0, tag)).post();

    // Implied constraint (stated in the reference too): every template fills all
    // its slots, so the sheets printed cover the total demand,
    // n_slots * sheets >= sum(demand).
    let total_demand: i32 = demand.iter().sum();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(
            vec![sheets.scaled(-n_slots)], -total_demand, tag))
        .post();

    let mut m = Model::new();
    m.put("production", production);
    m.put("layout", layout);
    m.minimise(sheets);
    m
}
