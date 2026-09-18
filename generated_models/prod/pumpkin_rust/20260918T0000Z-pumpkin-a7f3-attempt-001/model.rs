// Most profitable production plan under one shared capacity limit.
fn gcd(a: i32, b: i32) -> i32 {
    if b == 0 { a.abs() } else { gcd(b, a % b) }
}

fn lcm(a: i32, b: i32) -> i32 {
    a / gcd(a, b) * b
}

fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let a = inst.ints("a");
    let c_profit = inst.ints("c");
    let u = inst.ints("u");
    let b = inst.int("b");
    let n = a.len();

    let ceiling = *u.iter().max().unwrap_or(&0);
    let x = cp.ints(n, 0, ceiling);
    for j in 0..n {
        cp.le(vec![t(x[j])], u[j]);
    }

    // sum((1/a[j]) * x[j]) <= b, multiplied through by lcm(a) to stay integral.
    let scale = a.iter().fold(1, |acc, &v| lcm(acc, v));
    let coefficients: Vec<i32> = a.iter().map(|&v| scale / v).collect();
    cp.le(weighted(&coefficients, &x), b * scale);

    let profit = cp.sum(weighted(&c_profit, &x));

    let mut m = Model::new();
    m.put("x", x);
    m.put("total_profit", profit);
    m.maximise(profit);
    m
}
