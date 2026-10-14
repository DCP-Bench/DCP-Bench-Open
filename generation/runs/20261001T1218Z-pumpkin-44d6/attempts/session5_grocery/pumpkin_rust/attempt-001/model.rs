// Grocery: a kid buys num_items items. Adding the prices (in cents) gives the
// total price, and multiplying the prices in dollars gives the same total,
// i.e. the product of the prices in cents is total_price * 100^(num_items-1).
// Find the prices.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let total = inst.int("total_price");
    let k = inst.size("num_items");

    // The required product of the prices in cents. It can exceed the 32-bit
    // range Pumpkin's integers use, so it is computed here in 64 bits.
    let mut target: i64 = total as i64;
    for _ in 1..k {
        target *= 100;
    }

    // Prime factorisation of the product, by trial division.
    let mut primes: Vec<(i64, i32)> = Vec::new(); // (prime, exponent in target)
    let mut rest = target;
    let mut p: i64 = 2;
    while p * p <= rest {
        let mut e = 0;
        while rest % p == 0 {
            rest /= p;
            e += 1;
        }
        if e > 0 {
            primes.push((p, e));
        }
        p += 1;
    }
    if rest > 1 {
        primes.push((rest, 1));
    }

    // Each price divides the product (all prices are positive integers), and is
    // at most the total (the prices add up to it). The product constraint is
    // stated through the prime exponents of the prices: the product equals the
    // target exactly when, for every prime, the exponents of the prices add up to
    // the exponent in the target. This avoids multiplying 32-bit variables whose
    // product would overflow.
    let divisors: Vec<i32> = (1..=total).filter(|&d| target % d as i64 == 0).collect();
    let rows: Vec<Vec<i32>> = divisors
        .iter()
        .map(|&d| {
            let mut row = vec![d];
            for &(prime, _) in &primes {
                let mut e = 0;
                let mut v = d as i64;
                while v % prime == 0 {
                    v /= prime;
                    e += 1;
                }
                row.push(e);
            }
            row
        })
        .collect();

    // prices[i] is the price of item i in cents, between 1 and the total.
    let prices: Vec<Var> = (0..k).map(|_| solver.new_bounded_integer(1, total)).collect();
    // exponent[i][q] is the exponent of the q-th prime in prices[i].
    let exponent: Vec<Vec<Var>> = (0..k)
        .map(|_| primes.iter().map(|&(_, e)| solver.new_bounded_integer(0, e)).collect())
        .collect();

    // Each price is a divisor of the product, with its prime exponents.
    let factorised = solver.new_constraint_tag();
    for i in 0..k {
        let mut scope = vec![prices[i]];
        scope.extend(exponent[i].iter().copied());
        solver
            .add_constraint(pumpkin_solver::table(scope, rows.clone(), factorised))
            .post();
    }

    // Multiplying the prices gives the product: per prime, the exponents add up.
    let product = solver.new_constraint_tag();
    for (q, &(_, e)) in primes.iter().enumerate() {
        let column: Vec<Var> = (0..k).map(|i| exponent[i][q]).collect();
        solver
            .add_constraint(pumpkin_solver::equals(column, e, product))
            .post();
    }

    // Adding the prices gives the total price.
    let sum = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(prices.clone(), total, sum))
        .post();

    let mut m = Model::new();
    m.put("prices", prices);
    m
}
