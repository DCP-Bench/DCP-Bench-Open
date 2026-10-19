// csplib 084: Hadamard matrix Legendre pairs (2cc CSP) for odd l, m = (l-1)/2.
// Variables a_1..a_l and b_1..b_l take values in {-1, +1}.
// Each sign variable is an integer in -1..=1 that is not 0, and a Boolean literal
// p with p <-> (value == 1) for the pair constraints.

// Sign variable: an integer in {-1, +1} and its literal (true iff the value is +1).
fn sign_var(s: &mut Cadical) -> Res<(IntVar, Lit)> {
    let z = IntVar::new(-1..=1);
    // the value 0 is excluded
    let zb = z.equals(s, 0)?;
    let zero = lit_of(s, zb)?;
    s.add_clause([!zero])?;
    // with 0 excluded, value >= 0 means value == +1
    let pb = z.at_least(s, 0)?;
    let p = lit_of(s, pb)?;
    Ok((z, p))
}

// Literal e with e <-> (p == q).
fn xnor(s: &mut Cadical, p: Lit, q: Lit) -> Res<Lit> {
    let e = s.new_lit();
    s.add_clause([!e, !p, q])?;
    s.add_clause([!e, p, !q])?;
    s.add_clause([e, p, q])?;
    s.add_clause([e, !p, !q])?;
    Ok(e)
}

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let l = inst.size("l");
    let m = (l - 1) / 2;

    let mut a_vars = Vec::with_capacity(l);
    let mut a_lits = Vec::with_capacity(l);
    for _ in 0..l {
        let (z, p) = sign_var(s)?;
        a_vars.push(z);
        a_lits.push(p);
    }
    let mut b_vars = Vec::with_capacity(l);
    let mut b_lits = Vec::with_capacity(l);
    for _ in 0..l {
        let (z, p) = sign_var(s)?;
        b_vars.push(z);
        b_lits.push(p);
    }

    // For every s = 1..m, PAF(A, s) + PAF(B, s) = -2, where PAF(A, s) = sum_i a_i a_{i+s mod l}.
    // A product of two signs is +1 when the signs are equal and -1 otherwise, so with
    // E = number of equal pairs over both sequences, PAF(A,s) + PAF(B,s) = 2E - 2l.
    // So the condition is E = l - 1 for every s.
    for shift in 1..=m {
        let mut equal_pairs = LinExp::default();
        // the sum over both sequences of the products a_i a_{i+s} and b_i b_{i+s}
        for i in 0..l {
            let j = (i + shift) % l;
            let e = xnor(s, a_lits[i].clone(), a_lits[j].clone())?;
            equal_pairs += LinExp::from(e);
        }
        for i in 0..l {
            let j = (i + shift) % l;
            let e = xnor(s, b_lits[i].clone(), b_lits[j].clone())?;
            equal_pairs += LinExp::from(e);
        }
        post(s, equal_pairs, Comparator::Equal, (l - 1) as i64)?;
    }

    // a_1 + ... + a_l = 1 and b_1 + ... + b_l = 1
    let mut sum_a = LinExp::default();
    for z in &a_vars {
        sum_a += iv(z);
    }
    post(s, sum_a, Comparator::Equal, 1)?;

    let mut sum_b = LinExp::default();
    for z in &b_vars {
        sum_b += iv(z);
    }
    post(s, sum_b, Comparator::Equal, 1)?;

    let mut out = Out::new();
    out.put("a", &a_vars).put("b", &b_vars);
    Ok(out)
}
