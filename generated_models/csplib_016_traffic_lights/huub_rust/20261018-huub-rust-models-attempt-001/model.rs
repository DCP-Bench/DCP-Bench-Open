// CSPLib 016, traffic lights: a four-way junction with four vehicle lights (V1..V4)
// and four pedestrian lights (P1..P4). The lights output is [V1, V2, V3, V4, P1, P2, P3, P4].

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    // The allowed (V_i, P_i, V_i+1, P_i+1) combinations come from the instance.
    let tuples = inst.matrix("allowed_tuples");

    // Vehicle light states: 0=red, 1=red-yellow, 2=green, 3=yellow.
    // Pedestrian light states: 0=red, 1=green.
    let v = m.new_int_decisions(4, 0..=3);
    let p = m.new_int_decisions(4, 0..=1);

    // Every pair of consecutive lights, with light 5 wrapping to light 1, must be an allowed combination
    // for intersecting roads, and every other combination is disallowed.
    // Each light pair is a positive table over (V_i, P_i, V_i+1, P_i+1).
    for i in 0..4 {
        let j = (i + 1) % 4;
        m.table(vec![v[i], p[i], v[j], p[j]])
            .values(tuples.clone())
            .post()?;
    }

    let mut lights = v.clone();
    lights.extend(p.clone());

    let mut out = Out::new();
    out.put("lights", lights);
    Ok(out)
}
