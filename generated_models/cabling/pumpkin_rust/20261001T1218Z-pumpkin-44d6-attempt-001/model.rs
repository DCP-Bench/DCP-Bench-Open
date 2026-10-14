// Cabling: place devices in the slots of a rack, one device per slot, so that the
// total length of all the cables between devices is as short as possible. A cable
// run between two devices is as long as the distance between their slots, times
// the number of cables joining them.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n"); // number of devices, and of rack slots
    let n_i32 = n as i32;
    let devices = inst.strings("devices");
    // Each row of cable_struct is [device name, device name, number of cables]; a
    // row mixes strings and an integer, so it is read from the raw JSON.
    let cable_rows = inst
        .get("cable_struct")
        .as_array()
        .expect("instance field cable_struct: expected an array");
    let cables: Vec<(usize, usize, i32)> = cable_rows
        .iter()
        .map(|row| {
            let position_of = |name: &Value| -> usize {
                let name = name.as_str().expect("cable_struct: expected a device name");
                devices
                    .iter()
                    .position(|d| d == name)
                    .unwrap_or_else(|| panic!("cable_struct: unknown device {name}"))
            };
            let number = row[2].as_i64().expect("cable_struct: expected a cable count") as i32;
            (position_of(&row[0]), position_of(&row[1]), number)
        })
        .collect();
    let total_cables: i32 = cables.iter().map(|&(_, _, num)| num).sum();

    // x[d] is the slot of device d in the rack, counted from 0.
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, n_i32 - 1)).collect();
    // t[c] is the length of the cabling of row c, in 1 .. n * n as in the reference.
    let t: Vec<Var> = (0..cables.len())
        .map(|_| solver.new_bounded_integer(1, n_i32 * n_i32))
        .collect();
    // final_sum is the total cable length; its bound is the reference's.
    let final_sum = solver.new_bounded_integer(0, n_i32 * n_i32 * total_cables);

    // All devices are in different slots.
    let distinct = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::all_different(x.clone(), distinct))
        .post();

    // The cable length of a row is |x[a] - x[b]| * (number of cables): the
    // distance between the two slots, via signed difference and `absolute`.
    let signed_gap = solver.new_constraint_tag();
    let distance = solver.new_constraint_tag();
    let length = solver.new_constraint_tag();
    for (c, &(a, b, number)) in cables.iter().enumerate() {
        let gap = solver.new_bounded_integer(-(n_i32 - 1), n_i32 - 1);
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![x[a].scaled(1), x[b].scaled(-1), gap.scaled(-1)], 0, signed_gap))
            .post();
        let apart = solver.new_bounded_integer(0, n_i32 - 1);
        solver
            .add_constraint(pumpkin_solver::absolute(gap, apart, distance))
            .post();
        // t[c] == apart * number; a zero count would be a zero coefficient, so
        // it is posted as t[c] == 0 instead.
        let mut terms: Vec<Term> = vec![t[c].scaled(1)];
        if number != 0 {
            terms.push(apart.scaled(-number));
        }
        solver
            .add_constraint(pumpkin_solver::equals(terms, 0, length))
            .post();
    }

    // The total is the sum of the cable lengths.
    let mut terms: Vec<Term> = t.iter().map(|v| v.scaled(1)).collect();
    terms.push(final_sum.scaled(-1));
    let total = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, total))
        .post();

    let mut m = Model::new();
    m.put("final_sum", final_sum);
    m.minimise(final_sum);
    m
}
