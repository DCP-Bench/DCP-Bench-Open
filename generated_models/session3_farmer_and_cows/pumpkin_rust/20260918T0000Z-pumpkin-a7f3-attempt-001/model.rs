// Split the cows so each son gets his quota and the same total milk.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let num_cows = inst.size("num_cows");
    let num_sons = inst.size("num_sons");
    let quota = inst.ints("cows_per_son");

    // Cow i (1-based) yields i litres.
    let milk: Vec<i32> = (1..=num_cows as i32).collect();
    let total: i32 = milk.iter().sum();
    let share = total / num_sons as i32;

    let assignment = cp.ints(num_cows, 0, num_sons as i32 - 1);
    for son in 0..num_sons {
        let mine: Vec<Lit> = (0..num_cows).map(|i| cp.is(assignment[i], son as i32)).collect();
        cp.exactly(&mine, quota[son]);
        let target = cp.constant(share);
        cp.bool_sum_eq(&milk, &mine, target);
    }

    let mut m = Model::new();
    m.put("cow_assignments", assignment);
    m
}
