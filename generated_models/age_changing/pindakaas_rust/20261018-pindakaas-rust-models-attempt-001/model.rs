// Age changing: find my age m and my husband's age h (both whole, nonnegative numbers).
// Starting from my age and applying the four operations +2, /8, -3, *7 in some order gives
// his age h. Starting from his age and applying the same four operations in a different
// order gives my age m.

// Bound on both ages, derived from the statement rather than from a known answer. Each
// operation is affine with multiplier 7/8, 1/8, 7 or 1, so a composed chain has the form
// h = 7c/8 + K with |K| <= 2*7 + 3*7 = 35. The same holds for c = 7h/8 + K'. Eliminating h
// gives 15c/64 = 7K/8 + K' <= 65.625, so c <= 280, and h = 7c/8 + K <= 245 + 35 = 280.
const AGE_MAX: i64 = 280;

// The four operations of the description.
#[derive(Clone, Copy, Debug, PartialEq)]
enum Op {
    Add2,
    Div8,
    Sub3,
    Mul7,
}

const OPS: [Op; 4] = [Op::Add2, Op::Div8, Op::Sub3, Op::Mul7];

impl Op {
    // Interval of results when the input lies in lo..=hi. A /8 is exact: the input must be
    // a multiple of 8, so the result interval is rounded inwards.
    fn range(self, lo: i64, hi: i64) -> (i64, i64) {
        match self {
            Op::Add2 => (lo + 2, hi + 2),
            Op::Sub3 => (lo - 3, hi - 3),
            Op::Mul7 => (7 * lo, 7 * hi),
            Op::Div8 => ((lo + 7) / 8, hi / 8),
        }
    }
}

// All 24 orders in which the four operations can be applied once each.
fn all_orders() -> Vec<[Op; 4]> {
    let mut out = Vec::new();
    for a in 0..4 {
        for b in 0..4 {
            for c in 0..4 {
                for d in 0..4 {
                    let idx = [a, b, c, d];
                    let distinct = (0..4).all(|i| (0..i).all(|j| idx[i] != idx[j]));
                    if distinct {
                        out.push([OPS[a], OPS[b], OPS[c], OPS[d]]);
                    }
                }
            }
        }
    }
    out
}

// Exactly one of the literals is true.
fn one_of(s: &mut Cadical, lits: &[Lit]) -> Res {
    s.add_clause(lits.iter().copied())?;
    for (i, &a) in lits.iter().enumerate() {
        for &b in &lits[i + 1..] {
            s.add_clause([!a, !b])?;
        }
    }
    Ok(())
}

// cond -> applying the operations of `order` in turn to `from` gives `to`. Every step is
// posted in the safe conditional form, and each intermediate value is a nonnegative age.
fn chain(s: &mut Cadical, from: &IntVar, to: &IntVar, order: &[Op; 4], cond: Lit) -> Res {
    let mut cur = from.clone();
    let (mut lo, mut hi) = (0i64, AGE_MAX);
    for (k, op) in order.iter().enumerate() {
        let (nlo, nhi) = op.range(lo, hi);
        let (nlo, nhi) = (nlo.max(0), nhi);
        if nhi < nlo {
            // No nonnegative result exists for this order: the order cannot apply.
            s.add_clause([!cond])?;
            return Ok(());
        }
        let next = if k == 3 { to.clone() } else { IntVar::new(nlo..=nhi) };
        match op {
            Op::Add2 => post_if(s, &[cond], iv(&next) - iv(&cur), Comparator::Equal, 2)?,
            Op::Sub3 => post_if(s, &[cond], iv(&next) - iv(&cur), Comparator::Equal, -3)?,
            Op::Mul7 => post_if(s, &[cond], iv(&next) - scaled(&cur, 7), Comparator::Equal, 0)?,
            Op::Div8 => post_if(s, &[cond], iv(&cur) - scaled(&next, 8), Comparator::Equal, 0)?,
        }
        cur = next;
        lo = nlo;
        hi = nhi;
    }
    Ok(())
}

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // m: my age, h: my husband's age.
    let m = IntVar::new(0..=AGE_MAX);
    let h = IntVar::new(0..=AGE_MAX);
    let orders = all_orders();

    // Exactly one order takes my age to his, and exactly one order takes his age to mine.
    let mut to_h: Vec<Lit> = Vec::new();
    let mut to_m: Vec<Lit> = Vec::new();
    for _ in 0..orders.len() {
        to_h.push(s.new_lit());
        to_m.push(s.new_lit());
    }
    one_of(s, &to_h)?;
    one_of(s, &to_m)?;

    // The two orders are different: no order is used in both directions.
    for i in 0..orders.len() {
        s.add_clause([!to_h[i], !to_m[i]])?;
    }

    // Applying the four operations in some order to my age gives his age.
    // Applying the four operations in some order to his age gives my age.
    for (i, order) in orders.iter().enumerate() {
        chain(s, &m, &h, order, to_h[i])?;
        chain(s, &h, &m, order, to_m[i])?;
    }

    let mut out = Out::new();
    out.put("h", &h).put("m", &m);
    Ok(out)
}
