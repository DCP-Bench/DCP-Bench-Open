// Hadamard matrix Legendre pairs (2cc format) for odd l, with m = (l - 1) / 2.
// Variables a_1..a_l and b_1..b_l, each with domain {-1, +1}.
// The model uses 0-based arrays; index i + s wraps modulo l.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let l = inst.size("l");
    let half = (l - 1) / 2;

    // Variables a_1..a_l and b_1..b_l with domain {-1, +1}, i.e. the domain
    // -1..=1 without the value 0.
    let mut a: Vec<View<i64>> = Vec::with_capacity(l);
    let mut b: Vec<View<i64>> = Vec::with_capacity(l);
    for _ in 0..l {
        let x = m.new_int_decision(-1..=1);
        m.linear(x).ne(0).post()?;
        a.push(x);
    }
    for _ in 0..l {
        let x = m.new_int_decision(-1..=1);
        m.linear(x).ne(0).post()?;
        b.push(x);
    }

    // Constraints c_s: PAF(A, s) + PAF(B, s) = -2 for s = 1..m, where
    // PAF(A, s) = sum_i a_i * a_{i+s} (indices taken mod l).
    for s in 1..=half {
        let mut products: Vec<View<i64>> = Vec::with_capacity(2 * l);
        for i in 0..l {
            let j = (i + s) % l;
            let p = m.new_int_decision(-1..=1);
            m.mul(a[i], a[j]).result(p).post()?;
            products.push(p);
        }
        for i in 0..l {
            let j = (i + s) % l;
            let p = m.new_int_decision(-1..=1);
            m.mul(b[i], b[j]).result(p).post()?;
            products.push(p);
        }
        m.linear(products.iter().copied().sum::<IntLinearExp>())
            .eq(-2)
            .post()?;
    }

    // Linear constraints: a_1 + ... + a_l = 1 and b_1 + ... + b_l = 1.
    m.linear(a.iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    m.linear(b.iter().copied().sum::<IntLinearExp>()).eq(1).post()?;

    let mut out = Out::new();
    out.put("a", a).put("b", b);
    Ok(out)
}
