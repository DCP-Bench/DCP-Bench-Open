// Handshaking problem: Hilary and Jocelyn are married and invite num_couples couples who are friends for dinner.
// Persons 0 and 1 are Hilary and Jocelyn; persons 2k and 2k+1 form the k-th invited couple, so spouse(p) = p ^ 1.
// Every handshake is a Boolean literal per unordered pair of persons.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("num_couples");
    let people = 2 * (n + 1);

    // Nobody shakes hands with him or herself or with his or her spouse.
    // Only pairs that are not the same person and not spouses get a literal.
    let mut edge: Vec<Vec<Option<Lit>>> = vec![vec![None; people]; people];
    for p in 0..people {
        for q in (p + 1)..people {
            if q != (p ^ 1) {
                edge[p][q] = Some(s.new_lit());
            }
        }
    }

    // The hand count of each person is the number of handshakes they take part in.
    let mut hands: Vec<IntVar> = Vec::new();
    for p in 0..people {
        let mut e = LinExp::default();
        for q in 0..people {
            if q == p || q == (p ^ 1) {
                continue;
            }
            let (a, b) = if p < q { (p, q) } else { (q, p) };
            if let Some(l) = edge[a][b].clone() {
                e += LinExp::from(l);
            }
        }
        hands.push(define(s, e)?);
    }

    // Jocelyn stops the handshaking and asks how many hands each person has shaken (all but herself).
    // All the answers are different.
    let answers: Vec<IntVar> = hands
        .iter()
        .enumerate()
        .filter(|(p, _)| *p != 1)
        .map(|(_, h)| h.clone())
        .collect();
    all_different(s, &answers)?;

    // All the answers are different (redundant counting consequence, added for propagation): every answer
    // is at most 2n, so the 2n+1 answers are a permutation of 0..=2n and exactly 2n+1-k answers are at least k.
    let top = (2 * n) as i64;
    for k in 1..=top {
        let mut e = LinExp::default();
        for h in &answers {
            let b = reify_le(s, iv(h), k - 1)?;
            e += LinExp::from(!b);
        }
        post(s, e, Comparator::Equal, top + 1 - k)?;
    }

    // Print the number of hands Hilary has shaken (hil).
    let hil = hands[0].clone();
    let mut out = Out::new();
    out.put("hil", &hil);
    Ok(out)
}
