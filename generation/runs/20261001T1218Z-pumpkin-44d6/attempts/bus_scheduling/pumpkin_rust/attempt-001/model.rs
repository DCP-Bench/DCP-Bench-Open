// Bus scheduling: the day is cut into 4-hour slots and each bus works two
// successive slots; use as few buses as possible while covering each slot's demand.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let demands = inst.ints("demands"); // buses needed in each 4-hour slot
    let slots = demands.len();

    // x[i] is the number of buses that start working in slot i. As in the
    // reference, it ranges from 0 to the total demand.
    let ceiling: i32 = demands.iter().sum();
    let x: Vec<Var> = (0..slots).map(|_| solver.new_bounded_integer(0, ceiling)).collect();

    // A bus covers its starting slot and the next one (wrapping round from the
    // last slot to the first), so the buses covering slot i + 1 are those that
    // started in slot i or in slot i + 1, and they must meet the demand of slot
    // i + 1. Posted as -x[i] - x[i + 1] <= -demand, since Pumpkin only has "<=".
    let coverage = solver.new_constraint_tag();
    for i in 0..slots {
        let next = (i + 1) % slots;
        let terms: Vec<Term> = if next == i {
            vec![x[i].scaled(-2)] // a single slot: both buses are the same variable
        } else {
            vec![x[i].scaled(-1), x[next].scaled(-1)]
        };
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(terms, -demands[next], coverage))
            .post();
    }

    // Objective: the total number of buses, sum(x).
    let total_buses = solver.new_bounded_integer(0, ceiling * slots as i32);
    let mut terms: Vec<Term> = x.iter().map(|v| v.scaled(1)).collect();
    terms.push(total_buses.scaled(-1));
    let objective = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, objective))
        .post();

    let mut m = Model::new();
    m.put("x", x);
    m.minimise(total_buses);
    m
}
