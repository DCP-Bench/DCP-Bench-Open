// 2012 CMO problem: find the smallest a, at least a given minimum, such that for a
// positive integer b the difference a - b is a prime p and the product a * b is a
// perfect square n * n.

// The primes less than `limit`, found by trial division.
fn primes_below(limit: i32) -> Vec<i32> {
    (2..limit)
        .filter(|&k| (2..).take_while(|d| d * d <= k).all(|d| k % d != 0))
        .collect()
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let min_a = inst.int("min_a"); // a may not be smaller than this
    let max_val = inst.int("max_val"); // upper bound for every unknown

    // The variable bounds are the reference's: a from min_a, b positive, n and p up to max_val.
    let a = solver.new_bounded_integer(min_a, max_val);
    let b = solver.new_bounded_integer(1, max_val);
    let n = solver.new_bounded_integer(0, max_val);
    // p is a prime below max_val, so its domain is exactly those primes.
    let p = solver.new_sparse_integer(primes_below(max_val));

    // a >= b, posted as b - a <= 0.
    let order = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(
            vec![b.scaled(1), a.scaled(-1)], 0, order))
        .post();

    // p = a - b, posted as a - b - p = 0.
    let difference = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![a.scaled(1), b.scaled(-1), p.scaled(-1)], 0, difference))
        .post();

    // a * b = n * n: the product of a and b is a perfect square. Pumpkin's `times`
    // has three operands, so both products are given a variable and the two
    // variables are made equal.
    let product = solver.new_bounded_integer(0, max_val * max_val);
    let square = solver.new_bounded_integer(0, max_val * max_val);
    let multiply = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::times(a, b, product, multiply))
        .post();
    solver
        .add_constraint(pumpkin_solver::times(n, n, square, multiply))
        .post();
    let perfect_square = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![product.scaled(1), square.scaled(-1)], 0, perfect_square))
        .post();

    let mut m = Model::new();
    m.put("a", a);
    m.put("b", b);
    m.put("n", n);
    m.put("p", p);
    m.minimise(a);
    m
}
