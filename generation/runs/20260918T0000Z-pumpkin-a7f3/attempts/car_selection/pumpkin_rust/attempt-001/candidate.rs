// Match participants to cars they want, as many matches as possible.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let possible = inst.matrix("possible_assignments");
    let participants = possible.len();
    let cars = possible[0].len();

    let assignments = cp.bool_grid(participants, cars);
    for i in 0..participants {
        for j in 0..cars {
            if possible[i][j] == 0 {
                cp.eq(vec![t(assignments[i][j])], 0);
            }
        }
        cp.at_most(&assignments[i], 1);
    }
    for j in 0..cars {
        let column: Vec<Lit> = (0..participants).map(|i| assignments[i][j]).collect();
        cp.at_most(&column, 1);
    }

    let flat: Vec<Lit> = assignments.iter().flatten().copied().collect();
    let matched = cp.int(0, flat.len() as i32);
    let ones = vec![1; flat.len()];
    cp.bool_sum_eq(&ones, &flat, matched);

    let mut m = Model::new();
    m.put("assignments", assignments);
    m.maximise(matched);
    m
}
