// Handshaking (Halmos). Hilary and Jocelyn are married and invite num_couples
// couples who are friends, so there are num_couples + 1 couples in all.
// Person 0 is Hilary, person 1 is Jocelyn, and the spouse of person p is p ^ 1.
// They shake hands with each other. Each person's hand count is a variable;
// Hilary's count is the output "hil".

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
    // person takes part in. Nobody shakes hands with him or herself or with
    // his or her spouse.
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
    m.unique(answers.clone()).post()?;

    // The same fact, stated as a sum: distinct values from 0..=2n that cover
    // all 2n + 1 answerers sum to 0 + 1 + ... + 2n.
    let total: i64 = (0..=max_hands).sum();
    m.linear(answers.iter().copied().sum::<IntLinearExp>()).eq(total).post()?;

    // Derived redundant constraint, implied by the description (it holds in
    // every solution): in each invited couple, the two hand counts add up to
    // 2n. Argument: all the answers are different, so exactly one answerer
    // shook hands with 2n people. That person shook hands with everybody
    // except him or herself and his or her spouse, so the spouse shook hands
    // with nobody and has 0. Remove that couple and the same argument applies
    // to the rest, which gives the sum 2n for each couple.
    for k in 1..=n {
        eq2(m, hands[2 * k] + hands[2 * k + 1], max_hands)?;
    }

    let mut out = Out::new();
    out.put("hil", hands[0]);
    Ok(out)
}
