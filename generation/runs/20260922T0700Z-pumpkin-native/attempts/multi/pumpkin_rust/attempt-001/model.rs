// Cheapest multi-commodity shipping plan.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let supply = inst.matrix("supply");
    let demand = inst.matrix("demand");
    let limit = inst.matrix("limit");
    let cost = inst.cube("cost");
    let origins = supply.len();
    let destinations = demand.len();
    let products = supply[0].len();

    let max_supply = *supply.iter().flatten().max().unwrap_or(&0);
    // x[i][j][p]: units of product p shipped from origin i to destination j
    let mut x: Vec<Vec<Vec<Var>>> = Vec::new();
    for _ in 0..origins {
        let mut plane = Vec::new();
        for _ in 0..destinations {
            plane.push(
                (0..products)
                    .map(|_| solver.new_bounded_integer(0, max_supply))
                    .collect::<Vec<Var>>(),
            );
        }
        x.push(plane);
    }

    for i in 0..origins {
        for p in 0..products {
            let out: Vec<Var> = (0..destinations).map(|j| x[i][j][p]).collect();
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(out, supply[i][p], tag))
                .post();
        }
        for j in 0..destinations {
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    x[i][j].clone(), limit[i][j], tag))
                .post();
        }
    }
    for j in 0..destinations {
        for p in 0..products {
            // A lower bound, as an upper bound on the negated terms.
            let incoming: Vec<Term> = (0..origins).map(|i| x[i][j][p].scaled(-1)).collect();
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    incoming, -demand[j][p], tag))
                .post();
        }
    }

    let mut spend: Vec<Term> = Vec::new();
    for i in 0..origins {
        for j in 0..destinations {
            spend.extend(
                (0..products)
                    .filter(|&p| cost[i][j][p] != 0)
                    .map(|p| x[i][j][p].scaled(cost[i][j][p])),
            );
        }
    }
    let ceiling: i32 = supply.iter().flatten().sum::<i32>()
        * cost.iter().flatten().flatten().copied().max().unwrap_or(0);
    let total = solver.new_bounded_integer(0, ceiling);
    spend.push(total.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(spend, 0, tag)).post();

    let mut m = Model::new();
    m.put("total_cost", total);
    m.minimise(total);
    m
}
