// Bus scheduling (Progress City): find the minimum number of buses so that, in each
// 4-hour interval of the day, the buses available meet that interval's demand.
// Each bus works 8 successive hours, so it covers two consecutive 4-hour intervals,
// and the day is cyclic: the last interval is followed by the first.
// x[i] = number of buses that start their 8-hour shift in interval i.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let demands = inst.ints("demands");
    let n = demands.len();
    let dmax = demands.iter().copied().max().unwrap_or(0);

    // Buses starting in each interval. An optimal schedule never starts more buses in one
    // interval than the largest demand, since any surplus can be removed without breaking
    // a demand constraint; this bounds each x[i] by the instance's own data.
    let x: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(0..=dmax)).collect();

    // The buses available in each interval meet its demand. A bus that started in the
    // previous interval (cyclically) is still on duty in this one, so the buses available
    // in interval i are x[i] + x[i-1].
    for i in 0..n {
        let prev = (i + n - 1) % n;
        m.linear(x[i] + x[prev]).ge(demands[i]).post()?;
    }

    // Total number of buses, which is the objective to minimise.
    let total = m.new_int_decision(0..=(n as i64) * dmax);
    m.linear(x.iter().copied().sum::<IntLinearExp>()).eq(total).post()?;

    let mut out = Out::new();
    out.put("x", x);
    out.minimise(total);
    Ok(out)
}
