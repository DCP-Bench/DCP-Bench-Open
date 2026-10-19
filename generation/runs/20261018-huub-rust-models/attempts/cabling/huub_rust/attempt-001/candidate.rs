// Cabling: place the devices of a rack (one 1U device per position) in an order
// so that the sum of all cable lengths is as short as possible. Each cable joins
// two devices; its length is the distance between their positions.
// Output final_sum: the optimal sum of all cable lengths.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let devices: Vec<String> = inst.strings("devices");
    let cables = inst
        .get("cable_struct")
        .as_array()
        .expect("cable_struct must be an array");

    let index_of = |name: &str| -> usize {
        devices
            .iter()
            .position(|d| d == name)
            .expect("cable names a device that is not listed")
    };

    // Each device takes one position of the rack, and no two devices share one.
    let last = n as i64 - 1;
    let pos: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(0..=last)).collect();
    m.unique(pos.clone()).post()?;

    // Every cable contributes the distance between the positions of its two devices.
    // A row [device, device, count] stands for count cables between the two devices.
    let mut terms: Vec<IntLinearExp> = Vec::new();
    let mut cable_count: i64 = 0;
    for row in cables {
        let r = row.as_array().expect("cable row must be an array");
        let a = index_of(r[0].as_str().expect("first device of a cable must be a name"));
        let b = index_of(r[1].as_str().expect("second device of a cable must be a name"));
        let count = r[2].as_i64().expect("cable count must be an integer");
        let diff = m.new_int_decision(-last..=last);
        m.linear(pos[a] - pos[b]).eq(diff).post()?;
        let len = m.abs(diff).define();
        for _ in 0..count {
            terms.push(IntLinearExp::from(len));
            cable_count += 1;
        }
    }

    // The sum of all cable lengths is the objective.
    let ub = cable_count * last;
    let total = m.new_int_decision(0..=ub);
    m.linear(terms.into_iter().sum::<IntLinearExp>()).eq(total).post()?;

    let mut out = Out::new();
    out.put("final_sum", total);
    out.minimise(total);
    Ok(out)
}
