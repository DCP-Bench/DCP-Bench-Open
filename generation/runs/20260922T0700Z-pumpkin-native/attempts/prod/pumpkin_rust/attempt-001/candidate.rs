// Most profitable production plan under one shared capacity limit.
fn gcd(a: i32, b: i32) -> i32 {
    if b == 0 { a.abs() } else { gcd(b, a % b) }
}

fn lcm(a: i32, b: i32) -> i32 {
    a / gcd(a, b) * b
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let a = inst.ints("a");
    let c_profit = inst.ints("c");
    let u = inst.ints("u");
    let b = inst.int("b");
    let n = a.len();

    let ceiling = *u.iter().max().unwrap_or(&0);
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, ceiling)).collect();
    for j in 0..n {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![x[j].scaled(1)], u[j], tag))
            .post();
    }

    // sum((1/a[j]) * x[j]) <= b, multiplied through by lcm(a) to stay integral.
    let scale = a.iter().fold(1, |acc, &v| lcm(acc, v));
    let draw: Vec<Term> = (0..n)
        .filter(|&j| scale / a[j] != 0)
        .map(|j| x[j].scaled(scale / a[j]))
        .collect();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(draw, b * scale, tag))
        .post();

    let top: i32 = (0..n).map(|j| c_profit[j] * u[j]).sum();
    let profit = solver.new_bounded_integer(0, top);
    let mut earned: Vec<Term> = (0..n)
        .filter(|&j| c_profit[j] != 0)
        .map(|j| x[j].scaled(c_profit[j]))
        .collect();
    earned.push(profit.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(earned, 0, tag)).post();

    let mut m = Model::new();
    m.put("x", x);
    m.put("total_profit", profit);
    m.maximise(profit);
    m
}
