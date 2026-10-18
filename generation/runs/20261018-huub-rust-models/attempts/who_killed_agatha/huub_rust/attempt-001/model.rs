// Who killed Agatha. Three people: Agatha (0), the butler (1), Charles (2).
// hates[i][j] and richer[i][j] are 0/1 relations over these people
// (i hates j, i is richer than j). The killer is the one output.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let killer = m.new_int_decision(0..=2);

    let mut hates: Vec<Vec<View<i64>>> = Vec::new();
    let mut richer: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..3 {
        hates.push(m.new_int_decisions(3, 0..=1));
        richer.push(m.new_int_decisions(3, 0..=1));
    }

    // Agatha hates everybody except the butler.
    m.linear(hates[0][0]).eq(1).post()?;
    m.linear(hates[0][1]).eq(0).post()?;
    m.linear(hates[0][2]).eq(1).post()?;

    // Charles hates noone that Agatha hates.
    for x in 0..3 {
        m.linear(hates[2][x] + hates[0][x]).le(1).post()?;
    }

    // The butler hates everyone not richer than Aunt Agatha.
    for x in 0..3 {
        m.linear(hates[1][x] + richer[x][0]).ge(1).post()?;
    }

    // The butler hates everyone whom Agatha hates.
    for x in 0..3 {
        m.linear(hates[0][x]).le(hates[1][x]).post()?;
    }

    // Noone hates everyone.
    for x in 0..3 {
        m.linear(hates[x][0] + hates[x][1] + hates[x][2]).le(2).post()?;
    }

    // Someone in Dreadsbury Mansion killed Aunt Agatha: one indicator per person,
    // exactly one true, and the killer is the indicated person.
    let k_is: Vec<View<i64>> = m.new_int_decisions(3, 0..=1);
    m.linear(k_is[0] + k_is[1] + k_is[2]).eq(1).post()?;
    m.linear(killer - k_is[1] - k_is[2] * 2).eq(0).post()?;

    // A killer always hates, and is no richer than his victim (Agatha).
    for i in 0..3 {
        m.linear(k_is[i]).le(hates[i][0]).post()?;
        m.linear(richer[i][0] + k_is[i]).le(1).post()?;
    }

    let mut out = Out::new();
    out.put("killer", killer);
    Ok(out)
}
