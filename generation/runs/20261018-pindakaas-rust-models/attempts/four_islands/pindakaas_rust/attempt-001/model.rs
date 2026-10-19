// Four islands (DCP-Bench): a South Pacific nation with four islands A, B, C, D on a 2x2 map.
// Positions are A=0, B=1, C=2, D=3, so A is north-west, B north-east, C south-west and D south-east.
// Bridges: A-B and C-D are east-west; A-C and B-D are north-south.
// Find the name, export and tourist attraction of each island.
// Names are Pwana=0, Quero=1, Rayou=2, Skern=3; exports are alabaster=0, bananas=1, coconuts=2,
// durian fruit=3; attractions are resort hotel=0, ice skating rink=1, jai alai stadium=2, koala preserve=3.
// island[k] is the map position of island named k, export[j] the position of the island exporting j,
// attraction[a] the position of the island with attraction a.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let island: Vec<IntVar> = (0..4).map(|_| IntVar::new(0..=3)).collect();
    let export: Vec<IntVar> = (0..4).map(|_| IntVar::new(0..=3)).collect();
    let attraction: Vec<IntVar> = (0..4).map(|_| IntVar::new(0..=3)).collect();

    // Each of the four islands has a different name, export and attraction, one per map position.
    all_different(s, &island)?;
    all_different(s, &export)?;
    all_different(s, &attraction)?;

    // 1. The island noted for its koala preserve is due south of Pwana.
    table(
        s,
        &[attraction[3].clone(), island[0].clone()],
        &[vec![2, 0], vec![3, 1]],
    )?;

    // 2. The island with the largest alabaster quarry is due west of Quero.
    table(
        s,
        &[export[0].clone(), island[1].clone()],
        &[vec![0, 1], vec![2, 3]],
    )?;

    // 3. The island with the resort hotel is due east of the one that exports durian fruit.
    table(
        s,
        &[attraction[0].clone(), export[3].clone()],
        &[vec![1, 0], vec![3, 2]],
    )?;

    // 4. Skern and the island with the jai alai stadium are connected by a north-south bridge.
    table(
        s,
        &[island[3].clone(), attraction[2].clone()],
        &[vec![0, 2], vec![2, 0], vec![1, 3], vec![3, 1]],
    )?;

    // 5. Rayou and the island that exports bananas are connected by an east-west bridge.
    table(
        s,
        &[island[2].clone(), export[1].clone()],
        &[vec![0, 1], vec![1, 0], vec![2, 3], vec![3, 2]],
    )?;

    // 6. The islands noted for the South Pacific's largest ice skating rink and for the jai alai
    // stadium are not connected by a bridge.
    table(
        s,
        &[attraction[1].clone(), attraction[2].clone()],
        &[vec![0, 3], vec![3, 0], vec![1, 2], vec![2, 1]],
    )?;

    let mut out = Out::new();
    out.put("island", &island)
        .put("export", &export)
        .put("attraction", &attraction);
    Ok(out)
}
