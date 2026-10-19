// Handshaking (Halmos). Hilary and Jocelyn are married and invite num_couples
// couples who are friends, so there are num_couples + 1 couples in all.
// Person 0 is Hilary, person 1 is Jocelyn, and the spouse of person p is p ^ 1.
// Each person's hand count is a variable; Hilary's count is the output "hil".

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("num_couples");
    let people = 2 * (n + 1);
    let max_hands = (people - 2) as i64;

    // Nobody shakes hands with him or herself or with his or her spouse, so a
    // handshake variable exists only for an unordered pair that is not a couple.
    let mut hs: Vec<Vec<Option<View<bool>>>> = vec![vec![None; people]; people];
    for i in 0..people {
        for j in (i + 1)..people {
            if j != (i ^ 1) {
                hs[i][j] = Some(m.new_bool_decision());
            }
        }
    }

    // How many hands each person has shaken: the number of handshakes the
    // person takes part in.
    let mut hands: Vec<View<i64>> = Vec::with_capacity(people);
    for i in 0..people {
        let h = m.new_int_decision(0..=max_hands);
        let mut terms: Vec<View<bool>> = Vec::new();
        for j in 0..people {
            if j == i || j == (i ^ 1) {
                continue;
            }
            let b = if i < j { hs[i][j] } else { hs[j][i] };
            terms.push(b.unwrap());
        }
        m.linear(terms.iter().copied().sum::<IntLinearExp>()).eq(h).post()?;
        hands.push(h);
    }

    // All the answers are different. Jocelyn asks everyone else, so her own
    // count is not one of the answers. The other 2n + 1 people then take the
    // 2n + 1 values 0..=2n exactly once each.
    let answers: Vec<View<i64>> = hands
        .iter()
        .enumerate()
        .filter(|(i, _)| *i != 1)
        .map(|(_, h)| *h)
        .collect();
    m.unique(answers).post()?;

    let mut out = Out::new();
    out.put("hil", hands[0]);
    Ok(out)
}
