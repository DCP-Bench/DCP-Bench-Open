// Ages of the three sons of an old man (ages_of_the_sons). A1 >= A2 >= A3 are the ages,
// oldest first, all positive integers.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let _ = inst;
    let product: i64 = 36;
    let a1 = IntVar::new(1..=product);
    let a2 = IntVar::new(1..=product);
    let a3 = IntVar::new(1..=product);
    let xs = [a1.clone(), a2.clone(), a3.clone()];

    // The product of their ages is 36.
    let mut triples: Vec<Vec<i64>> = Vec::new();
    for a in 1..=product {
        for b in 1..=product {
            for c in 1..=product {
                if a * b * c == product {
                    triples.push(vec![a, b, c]);
                }
            }
        }
    }
    table(s, &xs, &triples)?;

    // The sons are listed from the oldest: A1 >= A2 >= A3.
    post(s, iv(&a2) - iv(&a1), Comparator::LessEq, 0)?;
    post(s, iv(&a3) - iv(&a2), Comparator::LessEq, 0)?;

    // The mathematician needs more information: the sum of their ages is not enough to
    // tell the sons apart. Each candidate triple (sorted, product 36) gets a literal that
    // holds when its sum equals the sum of the sons. At least two candidates share that sum.
    let sum = define(s, iv(&a1) + iv(&a2) + iv(&a3))?;
    let candidates: Vec<Vec<i64>> = triples
        .iter()
        .filter(|t| t[0] >= t[1] && t[1] >= t[2])
        .cloned()
        .collect();
    let mut lits: Vec<(Lit, Vec<i64>)> = Vec::new();
    for t in &candidates {
        let b = reify_eq(s, iv(&sum), t[0] + t[1] + t[2])?;
        lits.push((b, t.clone()));
    }
    let mut count = LinExp::default();
    for (b, _) in &lits {
        count += LinExp::from(b.clone());
    }
    post(s, count, Comparator::GreaterEq, 2)?;

    // The oldest son has blue eyes, so there is a unique oldest son: A1 > A2.
    post(s, iv(&a2) - iv(&a1), Comparator::LessEq, -1)?;

    // The mathematician got it: among the candidates with the same sum, only one has a
    // unique oldest son. Any candidate with a unique oldest son and that sum is the sons.
    for (b, t) in &lits {
        if t[0] > t[1] {
            post_if(s, &[b.clone()], iv(&a1), Comparator::Equal, t[0])?;
            post_if(s, &[b.clone()], iv(&a2), Comparator::Equal, t[1])?;
            post_if(s, &[b.clone()], iv(&a3), Comparator::Equal, t[2])?;
        }
    }

    let mut out = Out::new();
    out.put("A1", &a1).put("A2", &a2).put("A3", &a3);
    Ok(out)
}
