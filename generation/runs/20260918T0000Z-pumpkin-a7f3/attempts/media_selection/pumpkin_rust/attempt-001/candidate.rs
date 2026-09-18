// Cheapest set of media that still reaches every audience.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let incidence = inst.matrix("incidence_matrix");
    let costs = inst.ints("media_costs");
    let audiences = inst.len("target_audiences");
    let media = inst.len("advertising_media");

    let selected = cp.bools(media);
    for tgt in 0..audiences {
        let covers: Vec<i32> = (0..media).map(|m| incidence[tgt][m]).collect();
        // at least one covering medium is chosen
        cp.ge(weighted(&covers, &selected), 1);
    }

    let ceiling: i32 = costs.iter().sum();
    let spend = cp.int(0, ceiling);
    cp.bool_sum_eq(&costs, &selected, spend);

    let mut m = Model::new();
    m.put("is_selected", selected);
    m.put("min_total_cost", spend);
    m.minimise(spend);
    m
}
