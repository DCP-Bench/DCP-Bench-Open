// Bales of hay: n bales with unknown weights were weighed in all combinations of
// two, and the resulting pair weights were written down in numerical order without
// tracking which pair matched which weight. Find the weight of each bale.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let mut w = inst.ints("weights");
    w.sort();
    let m = w.len();
    assert_eq!(m, n * (n - 1) / 2, "weights must hold one entry per pair of bales");

    let wmin = w[0];
    let wmax = w[m - 1];
    // Each bale weight lies in a range derived from the data: for n >= 3, b_i is
    // half of (b_i + b_j) + (b_i + b_k) - (b_j + b_k), and every pair sum lies in [wmin, wmax].
    let (lo, hi) = if n >= 3 {
        ((2 * wmin - wmax).div_euclid(2), (2 * wmax - wmin + 1).div_euclid(2))
    } else {
        (0, wmax)
    };
    let bales: Vec<IntVar> = (0..n).map(|_| IntVar::new(lo..=hi)).collect();

    // The weights are all possible combinations of two bales: each pair sum
    // b_i + b_j for i < j is one of the given weights.
    let mut pair_sums: Vec<IntVar> = Vec::with_capacity(m);
    for i in 0..n {
        for j in (i + 1)..n {
            pair_sums.push(define(s, iv(&bales[i]) + iv(&bales[j]))?);
        }
    }

    // The weights were arranged in numerical order without keeping track of which
    // weight matched which pair: each pair sum takes exactly one weight, and each
    // weight is used by exactly one pair.
    let mut assign: Vec<Vec<Lit>> = Vec::with_capacity(m);
    for _ in 0..m {
        let row: Vec<Lit> = (0..m).map(|_| s.new_lit()).collect();
        assign.push(row);
    }
    for p in 0..m {
        let mut e = LinExp::default();
        for k in 0..m {
            e += LinExp::from(assign[p][k]);
        }
        post(s, e, Comparator::Equal, 1)?;
    }
    for k in 0..m {
        let mut e = LinExp::default();
        for p in 0..m {
            e += LinExp::from(assign[p][k]);
        }
        post(s, e, Comparator::Equal, 1)?;
    }
    for p in 0..m {
        for k in 0..m {
            post_if(s, &[assign[p][k]], iv(&pair_sums[p]), Comparator::Equal, w[k])?;
        }
    }

    let mut out = Out::new();
    out.put("bales", &bales);
    Ok(out)
}
