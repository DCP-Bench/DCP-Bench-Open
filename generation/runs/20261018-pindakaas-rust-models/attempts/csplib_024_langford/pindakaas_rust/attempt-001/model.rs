// Langford's problem: two sets of the numbers 1..k. Arrange the 2k numbers in one
// sequence so that the two 1's are one number apart, the two 2's two numbers apart,
// ..., and the two k's k numbers apart. Output sol is the sequence of 2k values.
//
// Encoding: for each number i, a Boolean per start position p, where p is the
// position of its first copy and its second copy sits at p + i + 1. Exactly one
// start per i. Each position is covered by exactly one number, and the value at a
// position is the sum of i times the covering literals of i.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let k = inst.int("k");
    let n = 2 * k;

    // Each number i has exactly one first position p, with 0 <= p and p + i + 1 < 2k.
    let mut starts: Vec<Vec<Lit>> = Vec::new();
    for i in 1..=k {
        let len = (n - i - 1) as usize;
        let lits: Vec<Lit> = (0..len).map(|_| s.new_lit()).collect();
        let mut one = LinExp::default();
        for l in &lits {
            one += LinExp::from(l.clone());
        }
        post(s, one, Comparator::Equal, 1)?;
        starts.push(lits);
    }

    // The sequence has 2k positions, each holding one value between 1 and k.
    let sol: Vec<IntVar> = (0..n).map(|_| IntVar::new(1..=k)).collect();

    // Each position is covered by exactly one number i: either as its first copy at j,
    // or as its second copy at j, which is the first copy at j - i - 1. The value at j
    // is the number that covers it.
    for j in 0..n {
        let mut occ = LinExp::default();
        let mut val = LinExp::default();
        for i in 1..=k {
            let row = &starts[(i - 1) as usize];
            let mut cover: Vec<Lit> = Vec::new();
            if j < row.len() as i64 {
                cover.push(row[j as usize].clone());
            }
            let q = j - i - 1;
            if q >= 0 && q < row.len() as i64 {
                cover.push(row[q as usize].clone());
            }
            for l in cover {
                occ += LinExp::from(l.clone());
                val += LinExp::from(l) * i;
            }
        }
        post(s, occ, Comparator::Equal, 1)?;
        post(s, val - iv(&sol[j as usize]), Comparator::Equal, 0)?;
    }

    let mut out = Out::new();
    out.put("sol", &sol);
    Ok(out)
}
