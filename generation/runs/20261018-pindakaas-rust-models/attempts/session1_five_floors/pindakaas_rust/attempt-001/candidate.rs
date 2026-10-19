// Problem session1_five_floors: Baker, Cooper, Fletcher, Miller and Smith live on the first five
// floors of an apartment house. Find the floor of each person (B, C, F, M, S).
// Satisfaction problem; floors are numbered 1 to 5.

// Not adjacent: x and y do not live on floors next to each other.
fn not_adjacent(s: &mut Cadical, x: &IntVar, y: &IntVar) -> Res<()> {
    let up = reify_eq(s, iv(x) - iv(y), 1)?;
    let down = reify_eq(s, iv(x) - iv(y), -1)?;
    s.add_clause([!up])?;
    s.add_clause([!down])?;
    Ok(())
}

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Baker does not live on the fifth floor.
    let b = IntVar::new(1..=4);
    // Cooper does not live on the first floor.
    let c = IntVar::new(2..=5);
    // Fletcher does not live on either the fifth or the first floor.
    let f = IntVar::new(2..=4);
    // Miller and Smith live on one of the first five floors.
    let m = IntVar::new(1..=5);
    let sm = IntVar::new(1..=5);

    // They all live on different floors.
    all_different(s, &[b.clone(), c.clone(), f.clone(), m.clone(), sm.clone()])?;

    // Miller lives on a higher floor than does Cooper.
    post(s, iv(&c) - iv(&m), Comparator::LessEq, -1)?;

    // Smith does not live on a floor adjacent to Fletcher's.
    not_adjacent(s, &sm, &f)?;

    // Fletcher does not live on a floor adjacent to Cooper's.
    not_adjacent(s, &f, &c)?;

    let mut out = Out::new();
    out.put("B", &b).put("C", &c).put("F", &f).put("M", &m).put("S", &sm);
    Ok(out)
}
