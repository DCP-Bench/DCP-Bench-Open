// Chess sets: a joinery makes small and large boxwood chess sets under a weekly
// limit of lathe-hours and of boxwood; choose how many of each to make to
// maximise the weekly profit.
//
// The instance has no fields: the machining hours, boxwood use, profits, weekly
// limits and the 0..100 range of each count are the problem's own constants,
// mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let (lathe_small, lathe_large, lathe_hours) = (3, 2, 160); // 4 lathes x 40 h
    let (wood_small, wood_large, wood_kg) = (1, 3, 200);
    let (profit_small, profit_large) = (5, 20);
    let max_count = 100;

    let small_set = solver.new_bounded_integer(0, max_count);
    let large_set = solver.new_bounded_integer(0, max_count);
    // The profit cannot exceed what the largest counts would earn.
    let max_profit = solver.new_bounded_integer(0, (profit_small + profit_large) * max_count);

    // Boxwood: 1 kg per small set and 3 kg per large set, at most 200 kg a week.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(
            vec![small_set.scaled(wood_small), large_set.scaled(wood_large)],
            wood_kg,
            tag,
        ))
        .post();

    // Lathe time: 3 hours per small set and 2 per large set, at most 160 hours.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(
            vec![small_set.scaled(lathe_small), large_set.scaled(lathe_large)],
            lathe_hours,
            tag,
        ))
        .post();

    // Profit: $5 per small set and $20 per large set.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![small_set.scaled(profit_small), large_set.scaled(profit_large), max_profit.scaled(-1)],
            0,
            tag,
        ))
        .post();

    let mut m = Model::new();
    m.put("small_set", small_set);
    m.put("large_set", large_set);
    m.put("max_profit", max_profit);
    m.maximise(max_profit);
    m
}
