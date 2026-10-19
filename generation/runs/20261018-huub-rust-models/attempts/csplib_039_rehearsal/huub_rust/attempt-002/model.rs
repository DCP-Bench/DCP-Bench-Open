// csplib_039_rehearsal: order the pieces of a concert so that the total time
// players are present but not playing is minimal.
// Players arrive immediately before the first piece they are involved in and
// depart immediately after the last one. Output rehearsal_order[i] is the piece
// rehearsed in the i-th slot. Sizes and data come from the instance:
// num_pieces, duration (per piece), rehearsal (player x piece, 1 = involved).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("num_pieces");
    let dur = inst.ints("duration");
    let reh = inst.matrix("rehearsal");
    let total: i64 = dur.iter().sum();
    let np = n as i64;

    // Each slot holds one piece and each piece is rehearsed in one slot.
    // order[i] is the piece in slot i, pos[p] is the slot of piece p.
    let order = m.new_int_decisions(n, 0..=(np - 1));
    let pos = m.new_int_decisions(n, 0..=(np - 1));
    m.unique(order.clone()).post()?;
    m.unique(pos.clone()).post()?;

    // pos is the inverse of order: the piece in slot i is order[i], so pos[order[i]] == i.
    // Encoded with element over pos, since the piece index is a variable.
    for i in 0..n {
        let p = m.element(pos.clone()).index(order[i]).define();
        m.linear(p).eq(i as i64).post()?;
    }

    // The pieces are rehearsed one after another with no gap: slot i+1 starts when
    // slot i ends. s[i] is the start of slot i and s[n] the end of the last slot.
    // The length of slot i is the duration of the piece in it, looked up by its index.
    // A gap between pieces never lowers the waiting time, so leaving gaps out does not
    // change the optimal orders.
    let s = m.new_int_decisions(n + 1, 0..=total);
    m.linear(s[0]).eq(0).post()?;
    for i in 0..n {
        let dv = m.element(dur.clone()).index(order[i]).define();
        m.linear(s[i] + dv - s[i + 1]).eq(0).post()?;
    }

    // Start and end time of each piece, read off its slot through pos.
    let starts: Vec<View<i64>> = (0..n)
        .map(|p| m.element(s[..n].to_vec()).index(pos[p]).define())
        .collect();
    let ends: Vec<View<i64>> = (0..n)
        .map(|p| m.element(s[1..].to_vec()).index(pos[p]).define())
        .collect();

    // A player is present from the start of the first piece he or she is involved in
    // to the end of the last one. Its span is the time present, with first and last
    // taken as the min start and max end over the pieces with rehearsal[j][p] == 1.
    // Players involved in no piece are never present and are left out.
    let mut spans: Vec<View<i64>> = Vec::new();
    for j in 0..reh.len() {
        let pieces: Vec<usize> = (0..n).filter(|&p| reh[j][p] == 1).collect();
        if pieces.is_empty() {
            continue;
        }
        let first = m.new_int_decision(0..=total);
        let last = m.new_int_decision(0..=total);
        m.minimum(pieces.iter().map(|&p| starts[p]).collect::<Vec<_>>())
            .result(first)
            .post()?;
        m.maximum(pieces.iter().map(|&p| ends[p]).collect::<Vec<_>>())
            .result(last)
            .post()?;
        let span = m.new_int_decision(0..=total);
        m.linear(last - first).eq(span).post()?;
        spans.push(span);
    }

    // Total waiting time is the sum of the spans minus the time players spend playing.
    // The time playing is the sum of the durations of the pieces each player is in,
    // a constant that the data fixes. The objective is the waiting time, with the
    // constant subtracted by the linear constraint below.
    let played: i64 = (0..reh.len())
        .map(|j| (0..n).filter(|&p| reh[j][p] == 1).map(|p| dur[p]).sum::<i64>())
        .sum();
    let obj_max = (reh.len() as i64) * total;
    let obj = m.new_int_decision(0..=obj_max);
    m.linear(spans.iter().copied().sum::<IntLinearExp>() - obj)
        .eq(played)
        .post()?;

    let mut out = Out::new();
    out.put("rehearsal_order", order.clone());
    out.minimise(obj);
    Ok(out)
}
