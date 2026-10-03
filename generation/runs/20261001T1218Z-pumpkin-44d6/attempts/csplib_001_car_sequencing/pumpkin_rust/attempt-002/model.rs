// Car sequencing: order the cars on an assembly line so that no option station is overloaded.

// At most `bound` of the literals are true (Pumpkin has no cardinality constraint,
// so this is a weighted sum of all-ones weights).
fn at_most(solver: &mut Solver, lits: &[Lit], bound: i32, tag: pumpkin_solver::core::proof::ConstraintTag) {
    solver
        .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
            vec![1; lits.len()], lits.to_vec(), bound, tag))
        .post();
}

// At least `bound` of the literals are true: at most len - bound of their negations are.
fn at_least(solver: &mut Solver, lits: &[Lit], bound: i32, tag: pumpkin_solver::core::proof::ConstraintTag) {
    let negated: Vec<Lit> = lits.iter().map(|&l| !l).collect();
    at_most(solver, &negated, lits.len() as i32 - bound, tag);
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let at_most_cars = inst.ints("at_most"); // cars needing option o allowed in a window ...
    let per_slots = inst.ints("per_slots"); // ... of this many consecutive slots
    let demand = inst.ints("demand"); // cars wanted of each type
    let requires = inst.matrix("requires"); // requires[t][o] = 1 if type t needs option o

    let n_cars: usize = demand.iter().sum::<i32>() as usize;
    let n_options = at_most_cars.len();
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

    // setup[s][o] is true exactly when the car in slot s needs option o, that is when
    // its type is one of the types with requires[t][o] == 1.
    let forward = solver.new_constraint_tag();
    let backward = solver.new_constraint_tag();
    let mut setup: Vec<Vec<Lit>> = Vec::new();
    for s in 0..n_cars {
        let mut row: Vec<Lit> = Vec::new();
        for o in 0..n_options {
            let needs = solver.new_literal();
            let mut types_needing: Vec<Lit> = vec![!needs];
            for t in 0..n_types {
                if requires[t][o] == 1 {
                    solver
                        .add_constraint(pumpkin_solver::clause(vec![!is_type[s][t], needs], forward))
                        .post();
                    types_needing.push(is_type[s][t]);
                }
            }
            solver
                .add_constraint(pumpkin_solver::clause(types_needing, backward))
                .post();
            row.push(needs);
        }
        setup.push(row);
    }

    // No station is overloaded: in every window of per_slots[o] consecutive slots,
    // at most at_most[o] cars require option o.
    let station = solver.new_constraint_tag();
    for o in 0..n_options {
        let window = per_slots[o] as usize;
        if window > n_cars {
            continue;
        }
        for start in 0..=(n_cars - window) {
            let needing: Vec<Lit> = (start..start + window).map(|s| setup[s][o]).collect();
            at_most(solver, &needing, at_most_cars[o], station);
        }
    }

    // Implied constraints, added only to help propagation (they follow from the
    // demands and the windows above). Let demand_o be the number of cars that
    // require option o, and room_o(k) = (k / per_slots) * at_most + min(at_most,
    // k % per_slots) the most cars that any k consecutive slots can hold with option
    // o. Then the first k slots and the last k slots each hold at most room_o(k)
    // such cars, and, because all demand_o of them must fit in the line, the first
    // k slots and the last k slots each hold at least demand_o - room_o(n - k).
    let implied = solver.new_constraint_tag();
    for o in 0..n_options {
        let demand_o: i32 = (0..n_types).map(|t| demand[t] * requires[t][o]).sum();
        let room = |k: usize| -> i32 {
            let q = per_slots[o] as usize;
            (k / q) as i32 * at_most_cars[o] + at_most_cars[o].min((k % q) as i32)
        };
        for k in 1..n_cars {
            let first: Vec<Lit> = (0..k).map(|s| setup[s][o]).collect();
            let last: Vec<Lit> = (n_cars - k..n_cars).map(|s| setup[s][o]).collect();
            if room(k) < k as i32 {
                at_most(solver, &first, room(k), implied);
                at_most(solver, &last, room(k), implied);
            }
            let rest = demand_o - room(n_cars - k);
            if rest > 0 {
                at_least(solver, &first, rest, implied);
                at_least(solver, &last, rest, implied);
            }
        }
    }

    let mut m = Model::new();
    m.put("sequence", sequence);
    m
}
