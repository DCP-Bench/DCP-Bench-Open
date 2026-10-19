// Aircraft landing problem: schedule the landing of aircraft on one runway, in a fixed landing sequence.
// Each aircraft lands within its time window [earliest_landing, latest_landing].
// Landing before the target time costs penalty_before per time unit, landing after it costs penalty_after per time unit.
// A minimum separation time must pass between the landings of any two aircraft, in sequence order.
// Objective: minimise the total penalty.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let earliest = inst.ints("earliest_landing");
    let latest = inst.ints("latest_landing");
    let target = inst.ints("target_landing");
    let pen_before = inst.ints("penalty_before");
    let pen_after = inst.ints("penalty_after");
    let sep = inst.matrix("separation_time");
    let n = earliest.len();

    // Each aircraft lands at a time within its time window.
    let land: Vec<View<i64>> = (0..n)
        .map(|i| m.new_int_decision(earliest[i]..=latest[i]))
        .collect();

    // Earliness and lateness with respect to the target landing time.
    let early: Vec<View<i64>> = (0..n)
        .map(|i| m.new_int_decision(0..=(target[i] - earliest[i]).max(0)))
        .collect();
    let late: Vec<View<i64>> = (0..n)
        .map(|i| m.new_int_decision(0..=(latest[i] - target[i]).max(0)))
        .collect();
    for i in 0..n {
        // The landing time differs from the target by earliness minus lateness.
        m.linear(land[i] + early[i] - late[i]).eq(target[i]).post()?;
    }

    // A minimum separation time must pass between the landings of any two aircraft.
    for i in 0..n {
        for j in (i + 1)..n {
            m.linear(land[j] - land[i]).ge(sep[i][j]).post()?;
        }
    }

    // Total penalty: earliness costs penalty_before, lateness costs penalty_after.
    let mut max_total = 0i64;
    for i in 0..n {
        max_total += pen_before[i] * (target[i] - earliest[i]).max(0)
            + pen_after[i] * (latest[i] - target[i]).max(0);
    }
    let total = m.new_int_decision(0..=max_total);
    let cost = (0..n)
        .map(|i| early[i] * pen_before[i] + late[i] * pen_after[i])
        .sum::<IntLinearExp>();
    m.linear(cost).eq(total).post()?;

    let mut out = Out::new();
    out.put("landing_times", land).put("total_penalty", total);
    out.minimise(total);
    Ok(out)
}
