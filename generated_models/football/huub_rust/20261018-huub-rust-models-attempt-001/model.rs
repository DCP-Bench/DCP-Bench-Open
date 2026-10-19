// Football squad selection: choose players from the groups with their prices (GBP millions,
// stored here in GBP thousands as integers) so that the total is as close to 30 million
// as possible without going over. Maximise the total price z.

// Goalkeepers (must buy 1 exactly): g1 0.73, g2 1.28, g3 3.88
// Defenders (must buy 2 or more): d1 0.92, d2 1.31, d3 1.62, d4 2.41, d5 2.79, d6 3.28, d7 3.91, d8 4.57
// Midfielders (must buy 3 or more): m1 1.8, m2 2.63, m3 3.17, m4 3.769, m5 4.14, m6 4.75, m7 5.38, m8 5.93, m9 6.78, m10 7.13
// Strikers (must buy 2 or more): s1 4.46, s2 6.47, s3 7.78, s4 8.39, s5 9.5
// Also, you must buy at least eleven players in total.
// The chairman gives an upper limit of GBP 30 million: the purchases add up to at most 30000 thousand.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let gk_price: [i64; 3] = [730, 1280, 3880];
    let def_price: [i64; 8] = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570];
    let mid_price: [i64; 10] = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130];
    let str_price: [i64; 5] = [4460, 6470, 7780, 8390, 9500];

    let gk: Vec<View<i64>> = gk_price.iter().map(|_| m.new_int_decision(0..=1)).collect();
    let def: Vec<View<i64>> = def_price.iter().map(|_| m.new_int_decision(0..=1)).collect();
    let mid: Vec<View<i64>> = mid_price.iter().map(|_| m.new_int_decision(0..=1)).collect();
    let str_: Vec<View<i64>> = str_price.iter().map(|_| m.new_int_decision(0..=1)).collect();

    // Goalkeepers: must buy 1 exactly.
    let gk_count: IntLinearExp = gk.iter().copied().sum();
    m.linear(gk_count).eq(1).post()?;

    // Defenders: must buy 2 or more.
    let def_count: IntLinearExp = def.iter().copied().sum();
    m.linear(def_count).ge(2).post()?;

    // Midfielders: must buy 3 or more.
    let mid_count: IntLinearExp = mid.iter().copied().sum();
    m.linear(mid_count).ge(3).post()?;

    // Strikers: must buy 2 or more.
    let str_count: IntLinearExp = str_.iter().copied().sum();
    m.linear(str_count).ge(2).post()?;

    // Also, you must buy at least eleven players in total.
    let all: Vec<View<i64>> = gk.iter().chain(def.iter()).chain(mid.iter()).chain(str_.iter()).copied().collect();
    let total_count: IntLinearExp = all.iter().copied().sum();
    m.linear(total_count).ge(11).post()?;

    // The chairman gives you an upper limit of GBP 30 million: the purchases must not go over it.
    let mut cost_terms: Vec<IntLinearExp> = Vec::new();
    for (x, p) in gk.iter().zip(gk_price.iter()) {
        cost_terms.push((*x * *p).into());
    }
    for (x, p) in def.iter().zip(def_price.iter()) {
        cost_terms.push((*x * *p).into());
    }
    for (x, p) in mid.iter().zip(mid_price.iter()) {
        cost_terms.push((*x * *p).into());
    }
    for (x, p) in str_.iter().zip(str_price.iter()) {
        cost_terms.push((*x * *p).into());
    }
    let cost: IntLinearExp = cost_terms.into_iter().sum();

    // Print out the total price of the players you have selected (z) in GBP thousands.
    let z = m.new_int_decision(0..=30000);
    m.linear(cost.clone()).le(30000).post()?;
    m.linear(cost).eq(z).post()?;

    let mut out = Out::new();
    out.put("z", z);
    out.maximise(z);
    Ok(out)
}
