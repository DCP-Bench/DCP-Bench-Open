// Best host: seat six guests around a round table so that no two neighbours
// do not get along. Guests: 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank.
// The output x lists the guests in seating order (seat 0 to seat 5, the last seat
// next to the first).

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n: usize = 6;
    let x: Vec<IntVar> = (0..n).map(|_| IntVar::new(0..=5)).collect();

    // Arrange the guests in a seating order: each guest sits in exactly one seat.
    all_different(s, &x)?;

    // Andrew will only sit next to Dave and Frank;
    // Betty will only sit next to Cara and Erica;
    // Cara will only sit next to Betty and Frank;
    // Dave will only sit next to Andrew and Erica;
    // Erica will only sit next to Betty and Dave;
    // Frank will only sit next to Andrew and Cara.
    // The allowed neighbour pairs are listed in both orders, since adjacency is symmetric.
    let allowed: Vec<Vec<i64>> = vec![
        vec![0, 3], vec![3, 0], // Andrew - Dave
        vec![0, 5], vec![5, 0], // Andrew - Frank
        vec![1, 2], vec![2, 1], // Betty - Cara
        vec![1, 4], vec![4, 1], // Betty - Erica
        vec![2, 5], vec![5, 2], // Cara - Frank
        vec![3, 4], vec![4, 3], // Dave - Erica
    ];

    // Seats are around a round table: seat i sits next to seat i+1, and seat 5 next to seat 0.
    // Every pair of neighbours must be an allowed pair, so no neighbours conflict.
    for i in 0..n {
        let j = (i + 1) % n;
        table(s, &[x[i].clone(), x[j].clone()], &allowed)?;
    }

    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
