// csplib_016_traffic_lights: a four-way traffic junction with eight traffic lights.
// Vehicle lights V1..V4 take states 0=red, 1=red-yellow, 2=green, 3=yellow.
// Pedestrian lights P1..P4 take states 0=red, 1=green.
// Output lights = [V1, V2, V3, V4, P1, P2, P3, P4].

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let allowed: Vec<Vec<i64>> = inst.matrix("allowed_tuples");

    let v: Vec<IntVar> = (0..4).map(|_| IntVar::new(0..=3)).collect();
    let p: Vec<IntVar> = (0..4).map(|_| IntVar::new(0..=1)).collect();

    // For i=1..4 (with V5=V1 and P5=P1), the combination (V_i, P_i, V_{i+1}, P_{i+1})
    // must be one of the safe combinations for intersecting roads; every other combination is disallowed.
    for i in 0..4 {
        let j = (i + 1) % 4;
        let xs = vec![v[i].clone(), p[i].clone(), v[j].clone(), p[j].clone()];
        table(s, &xs, &allowed)?;
    }

    let mut lights: Vec<IntVar> = v.clone();
    lights.extend(p.clone());

    let mut out = Out::new();
    out.put("lights", &lights);
    Ok(out)
}
