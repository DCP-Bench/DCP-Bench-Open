// Four islands puzzle: name, export and tourist attraction of each island.
// Islands Pwana, Quero, Rayou, Skern (island[0..4]); exports alabaster, bananas,
// coconuts, durian fruit (export[0..4]); attractions resort hotel, ice skating rink,
// jai alai stadium, koala preserve (attraction[0..4]). Each value is a map position:
// A=0, B=1, C=2, D=3. The map is a 2x2 grid: A (row 0, col 0), B (row 0, col 1),
// C (row 1, col 0), D (row 1, col 1). Bridges: A-B, A-C, B-D, C-D.

// Row and column of a map position, from a constant table (0-based element).
fn row_col(m: &mut Model, p: View<i64>) -> (View<i64>, View<i64>) {
    let r = m.element(vec![0i64, 0, 1, 1]).index(p).define();
    let c = m.element(vec![0i64, 1, 0, 1]).index(p).define();
    (r, c)
}

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Each island has a distinct map position.
    let island = m.new_int_decisions(4, 0..=3);
    m.unique(island.clone()).post()?;

    // Each export has a distinct map position.
    let export = m.new_int_decisions(4, 0..=3);
    m.unique(export.clone()).post()?;

    // Each tourist attraction has a distinct map position.
    let attraction = m.new_int_decisions(4, 0..=3);
    m.unique(attraction.clone()).post()?;

    // Row and column of each island, export and attraction position.
    let (ir0, ic0) = row_col(m, island[0]);
    let (ir1, ic1) = row_col(m, island[1]);
    let (ir2, ic2) = row_col(m, island[2]);
    let (ir3, ic3) = row_col(m, island[3]);
    let (er0, ec0) = row_col(m, export[0]);
    let (er1, ec1) = row_col(m, export[1]);
    let (er3, ec3) = row_col(m, export[3]);
    let (ar0, ac0) = row_col(m, attraction[0]);
    let (ar1, ac1) = row_col(m, attraction[1]);
    let (ar2, ac2) = row_col(m, attraction[2]);
    let (ar3, ac3) = row_col(m, attraction[3]);

    // The island noted for its koala preserve is due south of Pwana.
    // The koala island is the one at position attraction[3]; Pwana is island[0].
    m.linear(ar3 - ir0).eq(1).post()?;
    m.linear(ac3 - ic0).eq(0).post()?;

    // The island with the largest alabaster quarry is due west of Quero.
    // The alabaster island is export[0]; Quero is island[1].
    m.linear(ec0 - ic1).eq(-1).post()?;
    m.linear(er0 - ir1).eq(0).post()?;

    // The island with the resort hotel is due east of the one that exports durian fruit.
    // The hotel island is attraction[0]; the durian island is export[3].
    m.linear(ac0 - ec3).eq(1).post()?;
    m.linear(ar0 - er3).eq(0).post()?;

    // Skern and the island with the jai alai stadium are connected by a north-south bridge.
    // Skern is island[3]; the jai alai island is attraction[2].
    m.linear(ic3 - ac2).eq(0).post()?;
    m.linear(ir3 - ar2).ne(0).post()?;

    // Rayou and the island that exports bananas are connected by an east-west bridge.
    // Rayou is island[2]; the banana island is export[1].
    m.linear(ir2 - er1).eq(0).post()?;
    m.linear(ic2 - ec1).ne(0).post()?;

    // The islands noted for the ice skating rink and for the jai alai stadium are not
    // connected by a bridge. The rink is attraction[1]; the jai alai island is attraction[2].
    m.linear(ar1 - ar2).ne(0).post()?;
    m.linear(ac1 - ac2).ne(0).post()?;

    let mut out = Out::new();
    out.put("attraction", attraction)
        .put("export", export)
        .put("island", island);
    Ok(out)
}
