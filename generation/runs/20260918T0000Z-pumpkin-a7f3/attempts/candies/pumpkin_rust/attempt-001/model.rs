// One candy per child at least, more than a lower-rated neighbour, fewest overall.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let ratings = inst.ints("ratings");
    let n = ratings.len();

    let x = cp.ints(n, 1, n as i32);
    let z = cp.int(1, (n * n) as i32);
    cp.sum_eq(terms(&x), z);
    cp.ge(vec![t(z)], n as i32);

    for i in 1..n {
        if ratings[i - 1] > ratings[i] {
            cp.gt(vec![t(x[i - 1]), c(-1, x[i])], 0);
        } else if ratings[i - 1] < ratings[i] {
            cp.lt(vec![t(x[i - 1]), c(-1, x[i])], 0);
        }
    }

    let mut m = Model::new();
    m.put("x", x);
    m.put("z", z);
    m.minimise(z);
    m
}
