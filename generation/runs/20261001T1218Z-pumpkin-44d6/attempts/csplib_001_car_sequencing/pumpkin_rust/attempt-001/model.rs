// Car sequencing: order the cars on an assembly line so that no option station is overloaded.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let at_most = inst.ints("at_most"); // cars needing option o allowed in a window ...
    let per_slots = inst.ints("per_slots"); // ... of this many consecutive slots
    let demand = inst.ints("demand"); // cars wanted of each type
    let requires = inst.matrix("requires"); // requires[t][o] = 1 if type t needs option o

    let n_cars: usize = demand.iter().sum::<i32>() as usize;
    let n_options = at_most.len();
    let n_types = demand.len();

    // sequence[s] is the type of the car in slot s, numbered from 0.
    let sequence: Vec<Var> = (0..n_cars)
        .map(|_| solver.new_bounded_integer(0, n_types as i32 - 1))
        .collect();

    // is_type[s][t] is true exactly when slot s holds a car of type t.
    // Pumpkin has no count constraint, so the counts below go through these literals.
    let channel = solver.new_constraint_tag();
    let mut is_type: Vec<Vec<Lit>> = Vec::new();
    for s in 0..n_cars {
        let mut row: Vec<Lit> = Vec::new();
        for t in 0..n_types {
            let flag = solver.new_literal();
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![sequence[s].scaled(1)], t as i32, channel))
                .reify(flag);
            row.push(flag);
        }
        is_type.push(row);
    }

    // The number of cars of each type in the sequence equals the demand for that type.
    for t in 0..n_types {
        let column: Vec<Lit> = (0..n_cars).map(|s| is_type[s][t]).collect();
        let wanted = solver.new_bounded_integer(demand[t], demand[t]);
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::boolean_equals(
                vec![1; n_cars], column, wanted, tag))
            .post();
    }

    // No station is overloaded: in every window of per_slots[o] consecutive slots,
    // at most at_most[o] cars require option o. A slot needs option o exactly when
    // its car type is one of the types with requires[t][o] == 1, so the count of
    // such slots is a sum of the is_type literals of those types and no separate
    // setup table is needed.
    for o in 0..n_options {
        let window = per_slots[o] as usize;
        if window > n_cars {
            continue;
        }
        let station = solver.new_constraint_tag();
        for start in 0..=(n_cars - window) {
            let mut needing: Vec<Lit> = Vec::new();
            for s in start..start + window {
                for t in 0..n_types {
                    if requires[t][o] == 1 {
                        needing.push(is_type[s][t]);
                    }
                }
            }
            if needing.is_empty() {
                continue;
            }
            solver
                .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                    vec![1; needing.len()], needing, at_most[o], station))
                .post();
        }
    }

    let mut m = Model::new();
    m.put("sequence", sequence);
    m
}
