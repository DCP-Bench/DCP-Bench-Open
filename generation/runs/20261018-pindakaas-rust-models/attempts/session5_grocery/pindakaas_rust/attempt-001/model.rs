// Problem session5_grocery: a kid buys a number of items (num_items). The cashier charges
// total_price, once by adding the item prices and once by multiplying them. Both give the
// same total. Prices are in cents, so the product of the prices is the total in cents times
// 100 for each multiplication after the first: product = total_price * 100^(num_items - 1).
// Find the item prices in cents (prices).

// Literals for the values of x that divide p. Exactly one of them is true, since x takes one
// of these values (a table below restricts x to them).
fn value_lits(s: &mut Cadical, x: &IntVar, divs: &[i64]) -> Res<Vec<(i64, Lit)>> {
    let mut out: Vec<(i64, Lit)> = Vec::new();
    for &d in divs {
        if d <= x.max() {
            let bv = x.equals(s, d)?;
            out.push((d, lit_of(s, bv)?));
        }
    }
    Ok(out)
}

// Literals for the values of the product of two factors, each given as value literals. A
// partial product must divide p. The result has one literal per product value that occurs.
fn combine(
    s: &mut Cadical,
    a_list: &[(i64, Lit)],
    b_list: &[(i64, Lit)],
    p: i64,
) -> Res<Vec<(i64, Lit)>> {
    let mut out: std::collections::BTreeMap<i64, Lit> = std::collections::BTreeMap::new();
    for &(a, la) in a_list {
        for &(b, lb) in b_list {
            let m = a * b;
            if p % m != 0 {
                s.add_clause([!la, !lb])?;
                continue;
            }
            if !out.contains_key(&m) {
                let r = s.new_lit();
                out.insert(m, r);
            }
            let r = out[&m];
            s.add_clause([!la, !lb, r])?;
        }
    }
    // The product literal of the actual pair of values is true, and no other one is.
    for &(a, la) in a_list {
        for &(b, lb) in b_list {
            let m = a * b;
            if p % m != 0 {
                continue;
            }
            for (&v, &r) in &out {
                if v != m {
                    s.add_clause([!la, !lb, !r])?;
                }
            }
        }
    }
    Ok(out.into_iter().collect())
}

// Value literals for the product of xs, built as a balanced tree of pairs.
fn prod_lits(s: &mut Cadical, xs: &[IntVar], divs: &[i64], p: i64) -> Res<Vec<(i64, Lit)>> {
    if xs.len() == 1 {
        return value_lits(s, &xs[0], divs);
    }
    let h = xs.len() / 2;
    let a = prod_lits(s, &xs[..h], divs, p)?;
    let b = prod_lits(s, &xs[h..], divs, p)?;
    combine(s, &a, &b, p)
}

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("num_items");
    let t = inst.int("total_price");
    let p = t * 100i64.pow((n - 1) as u32);

    // The item prices are positive amounts in cents, one per item, and no price exceeds the
    // total. The prices multiply to p, so each price divides p.
    let divs: Vec<i64> = (1..=t).filter(|d| p % d == 0).collect();
    let prices: Vec<IntVar> = (0..n).map(|_| IntVar::new(1..=t)).collect();
    let single: Vec<Vec<i64>> = divs.iter().map(|&d| vec![d]).collect();
    for x in &prices {
        table(s, &[x.clone()], &single)?;
    }

    // The prices added up give the total price.
    let mut sum = LinExp::default();
    for x in &prices {
        sum += iv(x);
    }
    post(s, sum, Comparator::Equal, t)?;

    // The prices multiplied together give p. The two halves are multiplied, and their
    // products must multiply to p.
    if n > 1 {
        let h = n / 2;
        let left = prod_lits(s, &prices[..h], &divs, p)?;
        let right = prod_lits(s, &prices[h..], &divs, p)?;
        for &(a, la) in &left {
            for &(b, lb) in &right {
                if a * b != p {
                    s.add_clause([!la, !lb])?;
                }
            }
        }
    }

    let mut out = Out::new();
    out.put("prices", &prices);
    Ok(out)
}
