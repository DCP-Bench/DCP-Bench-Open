// Finding celebrities at a party: n guests, and graph[i][j] = 1 when guest i knows guest j.
// A celebrity is a guest that everybody at the party knows and that only knows other celebrities.
// At least one celebrity is present. celebrities[i] is 1 for a celebrity, in the input order.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let graph = inst.matrix("graph");
    let n = graph.len();
    let celeb: Vec<View<bool>> = m.new_bool_decisions(n);

    // At least one celebrity is present at the party.
    m.linear(celeb.iter().copied().sum::<IntLinearExp>()).ge(1).post()?;

    // A celebrity is a person that everybody at the party knows: a celebrity i needs
    // graph[j][i] = 1 for every guest j, so a guest that some guest does not know is no celebrity.
    for i in 0..n {
        for j in 0..n {
            if graph[j][i] == 0 {
                m.proposition(BoolFormula::Atom(!celeb[i])).post()?;
            }
        }
    }

    // A celebrity only knows other celebrities: if celebrity i knows j, then j is a celebrity too.
    for i in 0..n {
        for j in 0..n {
            if graph[i][j] == 1 {
                m.proposition(BoolFormula::Atom(!celeb[i]) | BoolFormula::Atom(celeb[j])).post()?;
            }
        }
    }

    // A guest that everybody knows and that only knows celebrities is a celebrity.
    for i in 0..n {
        if (0..n).all(|j| graph[j][i] == 1) {
            let mut clause = BoolFormula::Atom(celeb[i]);
            for j in 0..n {
                if graph[i][j] == 1 {
                    clause = clause | BoolFormula::Atom(!celeb[j]);
                }
            }
            m.proposition(clause).post()?;
        }
    }

    let mut out = Out::new();
    out.put("celebrities", celeb);
    Ok(out)
}
