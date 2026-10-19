// Media selection: allocate advertising budgets between media so that every
// target audience is reached by at least one selected medium, at minimum
// total campaign cost. Audience i is reached by medium j when
// incidence_matrix[i][j] = 1. Covering an audience twice is allowed.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.len("advertising_media");
    let audiences = inst.len("target_audiences");
    let costs = inst.ints("media_costs");
    let reach = inst.matrix("incidence_matrix");

    // Whether each medium is selected, as a Boolean and as a 0/1 integer.
    // The 0/1 integer is tied to the Boolean so the cost can be a linear sum.
    let sel: Vec<View<bool>> = (0..n).map(|_| m.new_bool_decision()).collect();
    let used: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(0..=1)).collect();
    for j in 0..n {
        m.linear(used[j]).eq(1).reified_by(sel[j]).post()?;
    }

    // Every target audience is reached by at least one selected medium.
    for i in 0..audiences {
        let covering: IntLinearExp = (0..n)
            .filter(|&j| reach[i][j] == 1)
            .map(|j| sel[j])
            .sum();
        m.linear(covering).ge(1).post()?;
    }

    // The campaign cost is the sum of the costs of the selected media.
    let total_max: i64 = costs.iter().sum();
    let cost = m.new_int_decision(0..=total_max);
    let weighted: IntLinearExp = (0..n).map(|j| used[j] * costs[j]).sum();
    m.linear(weighted).eq(cost).post()?;

    let mut out = Out::new();
    out.put("is_selected", sel).put("min_total_cost", cost);
    out.minimise(cost);
    Ok(out)
}
