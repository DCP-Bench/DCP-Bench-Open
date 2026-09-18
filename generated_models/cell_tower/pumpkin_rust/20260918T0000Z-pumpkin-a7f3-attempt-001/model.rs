// Build towers within budget to cover the most people.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let delta = inst.matrix("delta");
    let cost = inst.ints("cost");
    let population = inst.ints("population");
    let budget = inst.int("budget");
    let sites = cost.len();
    let regions = population.len();

    let build_tower = cp.bools(sites);
    let covered = cp.bools(regions);

    // A region only counts as covered if some chosen site reaches it.
    for j in 0..regions {
        let reach: Vec<i32> = (0..sites).map(|i| -delta[i][j]).collect();
        let mut row = vec![t(covered[j])];
        row.extend(weighted(&reach, &build_tower));
        cp.le(row, 0);
    }
    cp.bool_le(&cost, &build_tower, budget);

    let ceiling: i32 = population.iter().sum();
    let reached = cp.int(0, ceiling);
    cp.bool_sum_eq(&population, &covered, reached);

    let mut m = Model::new();
    m.put("build_tower", build_tower);
    m.put("total_population_covered", reached);
    m.maximise(reached);
    m
}
