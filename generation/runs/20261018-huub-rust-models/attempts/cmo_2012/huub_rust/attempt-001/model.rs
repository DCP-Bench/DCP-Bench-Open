// Problem cmo_2012: given positive integers a and b with a - b prime, a * b a perfect
// square n^2, and b > 0, find the smallest value of a no less than min_a.
// Output a, b, n, p, where p = a - b.

// Domains: a in min_a..=max_val, b in 1..=max_val - 2 (since a - b = p >= 2),
// n in 1..=max_val, p in 2..=max_val, and sq = a * b = n^2.
fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let min_a = inst.int("min_a");
    let max_val = inst.int("max_val");

    // Primes up to max_val, sieved from the instance bound.
    let lim = max_val as usize;
    let mut is_prime = vec![true; lim + 1];
    is_prime[0] = false;
    if lim >= 1 {
        is_prime[1] = false;
    }
    let mut d = 2usize;
    while d * d <= lim {
        if is_prime[d] {
            let mut k = d * d;
            while k <= lim {
                is_prime[k] = false;
                k += d;
            }
        }
        d += 1;
    }
    let primes: Vec<Vec<i64>> = (0..=lim)
        .filter(|&k| is_prime[k])
        .map(|k| vec![k as i64])
        .collect();

    let a = m.new_int_decision(min_a..=max_val);
    let b = m.new_int_decision(1..=max_val - 2);
    let p = m.new_int_decision(2..=max_val);
    let n = m.new_int_decision(1..=max_val);
    let sq = m.new_int_decision(1..=max_val * max_val);

    // a - b = p
    m.linear(a - b).eq(p).post()?;

    // p is one of the primes up to max_val.
    m.table(vec![p]).values(primes).post()?;

    // a * b = n^2
    m.mul(a, b).result(sq).post()?;
    m.mul(n, n).result(sq).post()?;

    // Implied by a * b = n^2 with 0 < b < a: b < n < a.
    m.linear(n - b).ge(1).post()?;
    m.linear(a - n).ge(1).post()?;

    let mut out = Out::new();
    out.put("a", a).put("b", b).put("n", n).put("p", p);
    out.minimise(a);
    Ok(out)
}
