// Problem cmo_2012: given positive integers a and b with a - b prime, a * b a perfect
// square n^2, and b > 0, find the smallest value of a no less than min_a.
// Output a, b, n, p, where p = a - b.

// Domains: a in min_a..=max_val, b in 1..=max_val, n and p in 0..=max_val,
// and sq = a * b = n^2 in 0..=max_val^2.
fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let min_a = inst.int("min_a");
    let max_val = inst.int("max_val");

    // Primality flags for 0..=max_val, sieved from the instance bound.
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
    let flags: Vec<i64> = is_prime.iter().map(|&pr| if pr { 1 } else { 0 }).collect();

    let a = m.new_int_decision(min_a..=max_val);
    let b = m.new_int_decision(1..=max_val);
    let p = m.new_int_decision(0..=max_val);
    let n = m.new_int_decision(0..=max_val);
    let sq = m.new_int_decision(0..=max_val * max_val);

    // a - b = p
    m.linear(a - b).eq(p).post()?;

    // p is prime: the flag at index p is 1.
    let is_p_prime = m.element(flags).index(p).define();
    m.linear(is_p_prime).eq(1).post()?;

    // a * b = n^2
    m.mul(a, b).result(sq).post()?;
    m.mul(n, n).result(sq).post()?;

    let mut out = Out::new();
    out.put("a", a).put("b", b).put("n", n).put("p", p);
    out.minimise(a);
    Ok(out)
}
