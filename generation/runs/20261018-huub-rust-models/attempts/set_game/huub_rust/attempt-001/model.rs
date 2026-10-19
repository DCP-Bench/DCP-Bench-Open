// Set (card game): pick three cards from the layout in the instance (cards_data, one
// row [number, fill, color, shape] per card, values 1..3) that form a set.
// Output winning_cards: the 0-based indices of the three cards.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let cards = inst.matrix("cards_data");
    let n = cards.len() as i64;

    // The winning set is three cards: indices in 0..n, all different.
    let w = m.new_int_decisions(3, 0..=(n - 1));
    m.unique(w.clone()).post()?;

    // For each one of the four categories of features (number, fill, color, shape),
    // the three cards must display that feature as either all the same, or all different.
    // With values 1..3, three values sum to a multiple of 3 exactly when they are all
    // the same or all different, so the sum equals 3 * q for some q in 1..3.
    for f in 0..4 {
        let col: Vec<i64> = cards.iter().map(|r| r[f]).collect();
        let mut v: Vec<View<i64>> = Vec::new();
        for k in 0..3 {
            let vk = m.element(col.clone()).index(w[k]).define();
            v.push(vk);
        }
        let q = m.new_int_decision(1..=3);
        m.linear(v[0] + v[1] + v[2] - q * 3).eq(0).post()?;
    }

    let mut out = Out::new();
    out.put("winning_cards", w);
    Ok(out)
}
