// csplib_039_rehearsal: order the pieces of a concert so that the total time
// players spend present but not playing is minimal.
// Players arrive immediately before the first piece they play in and leave
// immediately after the last one. Output rehearsal_order[i] is the piece
// rehearsed in slot i.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("num_pieces");
    let dur = inst.ints("duration");
    let reh = inst.matrix("rehearsal");
    let total: i64 = dur.iter().sum();
    let np = n as i64;

    // order[i] = piece in slot i; pos[p] = slot of piece p. Both are permutations.
    let order = m.new_int_decisions(n, 0..=(np - 1));
    let pos = m.new_int_decisions(n, 0..=(np - 1));
    m.unique(order.clone()).post()?;
    m.unique(pos.clone()).post()?;

    // pos is the inverse of order: pos[order[i]] == i.
    // The rehearsal slots are sequential, so the pieces are rehearsed back to back.
    for i in 0..n {
        let p = m.element(pos.clone()).index(order[i]).define();
        m.linear(p).eq(i as i64).post()?;
    }

    // Slot start times: S[0] = 0, S[i + 1] = S[i] + duration of the piece in slot i.
    // The piece in slot i has duration dur[order[i]].
    let s = m.new_int_decisions(n + 1, 0..=total);
    m.linear(s[0]).eq(0).post()?;
    for i in 0..n {
        let dv = m.element(dur.clone()).index(order[i]).define();
        m.linear(s[i] + dv - s[i + 1]).eq(0).post()?;
    }

    // Start and end time of each piece, looked up through its slot.
    let starts: Vec<View<i64>> = (0..n)
        .map(|p| m.element(s[..n].to_vec()).index(pos[p]).define())
        .collect();
    let ends: Vec<View<i64>> = (0..n)
        .map(|p| m.element(s[1..].to_vec()).index(pos[p]).define())
        .collect();

    // Waiting time of each player: from the start of the first piece the player
    // is in to the end of the last one, minus the time spent playing.
    // Here the span (last end - first start) is summed; the played time is
    // added as a constant below through the objective.
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

    // Total waiting time: the sum of the spans minus the time players spend playing.
    // The playing time is the sum of the durations of the pieces each player is in,
    // a constant of the instance.
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
