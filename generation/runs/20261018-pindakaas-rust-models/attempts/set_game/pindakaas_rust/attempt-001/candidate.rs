// Set card game: find a set of three cards among the cards in cards_data.
// Each card is [number, fill, color, shape], each feature takes a value in 1..3.
// Output winning_cards: the 0-based indices of the three cards of the set.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let cards = inst.matrix("cards_data");
    let n = cards.len() as i64;

    // The winning set is three cards, each a card of the layout.
    let w: Vec<IntVar> = (0..3).map(|_| IntVar::new(0..=n - 1)).collect();
    // Three different cards.
    all_different(s, &w)?;

    // For each feature, the three cards must display that feature as either all the same,
    // or all different: they must avoid two cards showing one version and the remaining card a different version.
    for f in 0..4 {
        let col: Vec<i64> = cards.iter().map(|c| c[f]).collect();
        let lo = *col.iter().min().expect("no cards");
        let hi = *col.iter().max().expect("no cards");

        // The feature value shown by each of the three cards.
        let mut v: Vec<IntVar> = Vec::new();
        for k in 0..3 {
            let vk = IntVar::new(lo..=hi);
            element_const(s, &w[k], &col, &vk)?;
            v.push(vk);
        }

        // Pairwise: do the two cards show the same version of this feature?
        let e01 = reify_eq(s, iv(&v[0]) - iv(&v[1]), 0)?;
        let e12 = reify_eq(s, iv(&v[1]) - iv(&v[2]), 0)?;
        let e02 = reify_eq(s, iv(&v[0]) - iv(&v[2]), 0)?;

        // All the same (all three pairs agree) or all different (no pair agrees):
        // the three pairwise agreements are equal, so exactly two agreeing pairs are excluded.
        s.add_clause([!e01, e12])?;
        s.add_clause([e01, !e12])?;
        s.add_clause([!e01, e02])?;
        s.add_clause([e01, !e02])?;
    }

    let mut out = Out::new();
    out.put("winning_cards", &w);
    Ok(out)
}
