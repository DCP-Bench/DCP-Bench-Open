// Problem: session1_thick_as_thieves. Following a robbery at Sparkles the Jeweller's,
// six suspects (artie, bill, crackitt, dodgy, edgy, fingers) are interviewed. The
// innocent ones tell the truth, the guilty ones lie. Find who is guilty.
// Output: each suspect is true when guilty.
//
// Encoding: g_x is "x is guilty", i_x is "x is innocent" (i_x + g_x = 1). Each
// statement is posted as "statement holds iff i_x", so an innocent suspect's statement
// is true and a guilty suspect's statement is false.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let g_a = m.new_bool_decision();
    let g_b = m.new_bool_decision();
    let g_c = m.new_bool_decision();
    let g_d = m.new_bool_decision();
    let g_e = m.new_bool_decision();
    let g_f = m.new_bool_decision();
    let i_a = m.new_bool_decision();
    let i_b = m.new_bool_decision();
    let i_c = m.new_bool_decision();
    let i_d = m.new_bool_decision();
    let i_e = m.new_bool_decision();
    let i_f = m.new_bool_decision();
    // not_b is "Bill is innocent" as a Boolean on Bill's guilt, used inside Dodgy's implication.
    let not_b = m.new_bool_decision();

    let all = [g_a, g_b, g_c, g_d, g_e, g_f];

    // The inspector supposed that the getaway car was barely big enough to hold two,
    // so at most two of them are guilty.
    m.linear(all.iter().copied().sum::<IntLinearExp>()).le(2).post()?;

    // Each suspect is innocent or guilty, not both.
    m.linear([i_a, g_a].iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    m.linear([i_b, g_b].iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    m.linear([i_c, g_c].iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    m.linear([i_d, g_d].iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    m.linear([i_e, g_e].iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    m.linear([i_f, g_f].iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    m.linear([not_b, g_b].iter().copied().sum::<IntLinearExp>()).eq(1).post()?;

    // ARTIE: "It wasn't me." True exactly when Artie is innocent.
    m.linear([g_a].iter().copied().sum::<IntLinearExp>()).eq(0).reified_by(i_a).post()?;

    // BILL: "Crackitt was in it up to his neck." True exactly when Bill is innocent.
    m.linear([g_c].iter().copied().sum::<IntLinearExp>()).eq(1).reified_by(i_b).post()?;

    // CRACKITT: "No I wasn't." True exactly when Crackitt is innocent.
    m.linear([g_c].iter().copied().sum::<IntLinearExp>()).eq(0).reified_by(i_c).post()?;

    // DODGY: "If Crackitt did it, Bill did it with him." The implication is false only
    // when Crackitt is guilty and Bill is not. True exactly when Dodgy is innocent.
    m.linear([g_c, not_b].iter().copied().sum::<IntLinearExp>()).le(1).reified_by(i_d).post()?;

    // EDGY: "Nobody did it alone." True exactly when the number of guilty is not one.
    m.linear(all.iter().copied().sum::<IntLinearExp>()).ne(1).reified_by(i_e).post()?;

    // FINGERS: "That's right: it was Artie and Dodgy together." True exactly when Artie
    // and Dodgy are both guilty and exactly two are guilty.
    let artie_and_dodgy = m.new_bool_decision();
    let two_guilty = m.new_bool_decision();
    m.linear([g_a, g_d].iter().copied().sum::<IntLinearExp>()).eq(2).reified_by(artie_and_dodgy).post()?;
    m.linear(all.iter().copied().sum::<IntLinearExp>()).eq(2).reified_by(two_guilty).post()?;
    m.linear([artie_and_dodgy, two_guilty].iter().copied().sum::<IntLinearExp>())
        .eq(2)
        .reified_by(i_f)
        .post()?;

    let mut out = Out::new();
    out.put("artie", g_a)
        .put("bill", g_b)
        .put("crackitt", g_c)
        .put("dodgy", g_d)
        .put("edgy", g_e)
        .put("fingers", g_f);
    Ok(out)
}
