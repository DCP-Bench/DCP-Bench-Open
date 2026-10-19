// Chess set production: how many small and large boxwood chess sets to make each week
// so as to maximise profit. Declared outputs: small_set, large_set, max_profit.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let _ = inst;

    // Number of small and large sets made per week.
    let small = m.new_int_decision(0..=200);
    let large = m.new_int_decision(0..=200);

    // Lathe time: a small set needs 3 hours of machining and a large set 2 hours;
    // four lathes with operators working 40 hours a week give 160 lathe-hours per week.
    // Machining is 3 * small + 2 * large <= 160.
    m.linear(small * 3 + large * 2).le(160).post()?;

    // Boxwood: a small set needs 1 kg and a large set 3 kg; only 200 kg per week can be obtained.
    // Boxwood is small + 3 * large <= 200.
    m.linear(small + large * 3).le(200).post()?;

    // Profit: each small set yields $5 and each large set $20, to be maximised.
    let profit = m.new_int_decision(0..=5000);
    m.linear(small * 5 + large * 20).eq(profit).post()?;

    let mut out = Out::new();
    out.put("small_set", small)
        .put("large_set", large)
        .put("max_profit", profit);
    out.maximise(profit);
    Ok(out)
}
