// Buy every project its hours from the people who have them, at least cost.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let supply = inst.ints("supply");
    let demand = inst.ints("demand");
    let cost = inst.matrix("cost");
    let limit = inst.matrix("limit");
    let people = supply.len();
    let projects = demand.len();

    // 0..10 hours per pairing is the bound the reference declares.
    let assign = cp.grid(people, projects, 0, 10);
    for i in 0..people {
        cp.eq(terms(&assign[i]), supply[i]);
        for j in 0..projects {
            cp.le(vec![t(assign[i][j])], limit[i][j]);
        }
    }
    for j in 0..projects {
        let column: Vec<Var> = (0..people).map(|i| assign[i][j]).collect();
        cp.eq(terms(&column), demand[j]);
    }

    let mut spend: Vec<Term> = Vec::new();
    for i in 0..people {
        spend.extend(weighted(&cost[i], &assign[i]));
    }
    let total = cp.sum(spend);

    let mut m = Model::new();
    m.put("assign", assign);
    m.put("total_cost", total);
    m.minimise(total);
    m
}
