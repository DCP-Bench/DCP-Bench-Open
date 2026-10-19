// Best host: seat six dinner guests around a round table so that as few neighbouring
// pairs as possible do not get along. Guests: 0 Andrew, 1 Betty, 2 Cara, 3 Dave,
// 4 Erica, 5 Frank. The output x is the seating order: x[seat] is the guest in that seat.
// The instance has no fields; the seat count and the "will only sit next to" lists are
// fixed by the statement, so they are written here as problem constants.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Six seats, six guests, one guest per seat.
    const N: usize = 6;

    // Who gets along with whom, from the statement (0-based guests).
    // Andrew: Dave, Frank; Betty: Cara, Erica; Cara: Betty, Frank;
    // Dave: Andrew, Erica; Erica: Betty, Dave; Frank: Andrew, Cara.
    let get_along: [[i64; N]; N] = [
        // Andrew
        [0, 0, 0, 1, 0, 1],
        // Betty
        [0, 0, 1, 0, 1, 0],
        // Cara
        [0, 1, 0, 0, 0, 1],
        // Dave
        [1, 0, 0, 0, 1, 0],
        // Erica
        [0, 1, 0, 1, 0, 0],
        // Frank
        [1, 0, 1, 0, 0, 0],
    ];

    // Seating order: each seat holds one guest, every guest sits once.
    let x = m.new_int_decisions(N, 0..=(N as i64) - 1);
    m.unique(x.clone()).post()?;

    // Two guests seated next to each other who do not get along create conflict.
    // ok[i] = 1 when the guests in seat i and seat i+1 get along (seat 5 sits next to seat 0).
    // The table lists every pair of guests with its get-along flag.
    let mut rows: Vec<Vec<i64>> = Vec::new();
    for a in 0..N {
        for b in 0..N {
            rows.push(vec![a as i64, b as i64, get_along[a][b]]);
        }
    }
    let mut ok = Vec::new();
    for i in 0..N {
        let j = (i + 1) % N;
        let flag = m.new_int_decision(0..=1);
        m.table(vec![x[i], x[j], flag]).values(rows.clone()).post()?;
        ok.push(flag);
    }

    // Minimise the conflicts at dinner: conflicts + neighbouring pairs that get along = number of seats.
    let conflicts = m.new_int_decision(0..=N as i64);
    m.linear(ok.iter().copied().sum::<IntLinearExp>() + conflicts)
        .eq(N as i64)
        .post()?;

    let mut out = Out::new();
    out.put("x", x);
    out.minimise(conflicts);
    Ok(out)
}
