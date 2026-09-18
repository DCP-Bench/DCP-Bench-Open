// Cheapest multi-commodity shipping plan.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
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
            plane.push(cp.ints(products, 0, max_supply));
        }
        x.push(plane);
    }

    for i in 0..origins {
        for p in 0..products {
            let out: Vec<Var> = (0..destinations).map(|j| x[i][j][p]).collect();
            cp.le(terms(&out), supply[i][p]);
        }
        for j in 0..destinations {
            cp.le(terms(&x[i][j]), limit[i][j]);
        }
    }
    for j in 0..destinations {
        for p in 0..products {
            let incoming: Vec<Var> = (0..origins).map(|i| x[i][j][p]).collect();
            cp.ge(terms(&incoming), demand[j][p]);
        }
    }

    let mut spend: Vec<Term> = Vec::new();
    for i in 0..origins {
        for j in 0..destinations {
            spend.extend(weighted(&cost[i][j], &x[i][j]));
        }
    }
    let ceiling: i32 = supply.iter().flatten().sum::<i32>()
        * cost.iter().flatten().flatten().copied().max().unwrap_or(0);
    let total = cp.int(0, ceiling);
    cp.sum_eq(spend, total);

    let mut m = Model::new();
    m.put("total_cost", total);
    m.minimise(total);
    m
}
