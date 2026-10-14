// Warehouse location: choose which warehouses to open and assign every store to
// one warehouse, within each warehouse's capacity, so that the opening cost of
// the open warehouses plus the supply costs of all stores is as small as possible.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n_suppliers = inst.size("n_suppliers"); // number of candidate warehouses
    let n_stores = inst.size("n_stores");
    let building_cost = inst.int("building_cost"); // cost of keeping one warehouse open
    let capacity = inst.ints("capacity"); // capacity[w]: most stores warehouse w can supply
    let cost_matrix = inst.matrix("cost_matrix"); // cost_matrix[s][w]: supplying store s from warehouse w

    // assigned[s][w] is true when store s is supplied by warehouse w.
    let assigned: Vec<Vec<Lit>> = (0..n_stores)
        .map(|_| (0..n_suppliers).map(|_| solver.new_literal()).collect())
        .collect();

    // supplier_assignment[s] is the warehouse that supplies store s, counted from 0.
    let supplier_assignment: Vec<Var> = (0..n_stores)
        .map(|_| solver.new_bounded_integer(0, n_suppliers as i32 - 1))
        .collect();

    // Each store is supplied by exactly one warehouse, and supplier_assignment[s]
    // is that warehouse's number: supplier_assignment[s] = sum(w * assigned[s][w]).
    let one_supplier = solver.new_constraint_tag();
    let channel = solver.new_constraint_tag();
    for s in 0..n_stores {
        solver
            .add_constraint(pumpkin_solver::clause(assigned[s].clone(), one_supplier))
            .post();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                vec![1; n_suppliers], assigned[s].clone(), 1, one_supplier))
            .post();
        let mut terms: Vec<Term> = vec![supplier_assignment[s].scaled(1)];
        for w in 1..n_suppliers {
            terms.push(assigned[s][w].get_integer_variable().scaled(-(w as i32)));
        }
        solver
            .add_constraint(pumpkin_solver::equals(terms, 0, channel))
            .post();
    }

    // The number of stores a warehouse supplies cannot exceed its capacity.
    let capacities = solver.new_constraint_tag();
    for w in 0..n_suppliers {
        let stores_of_w: Vec<Lit> = (0..n_stores).map(|s| assigned[s][w]).collect();
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                vec![1; n_stores], stores_of_w, capacity[w], capacities))
            .post();
    }

    // A warehouse is open if and only if it supplies at least one store.
    let open_warehouses: Vec<Lit> = (0..n_suppliers).map(|_| solver.new_literal()).collect();
    let opening = solver.new_constraint_tag();
    for w in 0..n_suppliers {
        // supplying a store means being open
        for s in 0..n_stores {
            solver
                .add_constraint(pumpkin_solver::clause(vec![!assigned[s][w], open_warehouses[w]], opening))
                .post();
        }
        // being open means supplying some store
        let mut some_store: Vec<Lit> = vec![!open_warehouses[w]];
        some_store.extend((0..n_stores).map(|s| assigned[s][w]));
        solver
            .add_constraint(pumpkin_solver::clause(some_store, opening))
            .post();
    }

    // total_cost = supply costs of all stores + building_cost per open warehouse.
    // Its bounds come from the cheapest and dearest choice for every store and
    // from opening none or all of the warehouses.
    let warehouses = n_suppliers as i32;
    let cheapest: i32 = cost_matrix.iter().map(|row| *row.iter().min().unwrap()).sum();
    let dearest: i32 = cost_matrix.iter().map(|row| *row.iter().max().unwrap()).sum();
    let total_cost = solver.new_bounded_integer(
        cheapest + warehouses * building_cost.min(0),
        dearest + warehouses * building_cost.max(0),
    );
    // Terms with a zero coefficient are left out because Pumpkin cannot take them.
    let mut terms: Vec<Term> = vec![total_cost.scaled(-1)];
    for s in 0..n_stores {
        for w in 0..n_suppliers {
            if cost_matrix[s][w] != 0 {
                terms.push(assigned[s][w].get_integer_variable().scaled(cost_matrix[s][w]));
            }
        }
    }
    if building_cost != 0 {
        for w in 0..n_suppliers {
            terms.push(open_warehouses[w].get_integer_variable().scaled(building_cost));
        }
    }
    let objective = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, objective))
        .post();

    let mut m = Model::new();
    m.put("total_cost", total_cost);
    m.put("open_warehouses", open_warehouses);
    m.put("supplier_assignment", supplier_assignment);
    m.minimise(total_cost);
    m
}
