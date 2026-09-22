// Buy every project its hours from the people who have them, at least cost.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let supply = inst.ints("supply");
    let demand = inst.ints("demand");
    let cost = inst.matrix("cost");
    let limit = inst.matrix("limit");
    let people = supply.len();
    let projects = demand.len();

    // 0..10 hours per pairing is the bound the reference declares.
    let assign: Vec<Vec<Var>> = (0..people)
        .map(|_| (0..projects).map(|_| solver.new_bounded_integer(0, 10)).collect())
        .collect();
    for i in 0..people {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(assign[i].clone(), supply[i], tag))
            .post();
        for j in 0..projects {
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![assign[i][j].scaled(1)], limit[i][j], tag))
                .post();
        }
    }
    for j in 0..projects {
        let column: Vec<Var> = (0..people).map(|i| assign[i][j]).collect();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(column, demand[j], tag))
            .post();
    }

    let ceiling: i32 = (0..people)
        .flat_map(|i| (0..projects).map(move |j| (i, j)))
        .map(|(i, j)| cost[i][j] * 10)
        .sum();
    let total = solver.new_bounded_integer(0, ceiling);
    let mut spend: Vec<Term> = (0..people)
        .flat_map(|i| (0..projects).map(move |j| (i, j)))
        .filter(|&(i, j)| cost[i][j] != 0)
        .map(|(i, j)| assign[i][j].scaled(cost[i][j]))
        .collect();
    spend.push(total.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(spend, 0, tag)).post();

    let mut m = Model::new();
    m.put("assign", assign);
    m.put("total_cost", total);
    m.minimise(total);
    m
}
