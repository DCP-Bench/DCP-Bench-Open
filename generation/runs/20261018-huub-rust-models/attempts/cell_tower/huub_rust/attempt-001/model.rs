// Cell tower coverage: choose which candidate sites get a tower so that the cost of the
// towers stays within the budget and the population covered by them is as large as possible.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let cost = inst.ints("cost");
    let population = inst.ints("population");
    let delta = inst.matrix("delta"); // delta[site][region] = 1 if the site's signal reaches the region
    let budget = inst.int("budget");
    let sites = cost.len();
    let regions = population.len();

    // Decide whether a tower is built at each site.
    let build_tower: Vec<View<bool>> = (0..sites).map(|_| m.new_bool_decision()).collect();

    // 0/1 integer copy of each decision, so it can be used in weighted sums.
    let mut built: Vec<View<i64>> = Vec::with_capacity(sites);
    for &b in &build_tower {
        let v = m.new_int_decision(0..=1);
        m.linear(IntLinearExp::from(b)).eq(v).post()?;
        built.push(v);
    }

    // Only a limited number of towers can be built: the total cost stays within the budget.
    let spend: IntLinearExp = built
        .iter()
        .copied()
        .zip(cost.iter().copied())
        .map(|(v, c)| v * c)
        .sum();
    m.linear(spend).le(budget).post()?;

    // A region is covered when at least one tower built at a site that reaches it covers it.
    let mut covered: Vec<View<i64>> = Vec::with_capacity(regions);
    for r in 0..regions {
        let c = m.new_int_decision(0..=1);
        let reaching: Vec<usize> = (0..sites).filter(|&i| delta[i][r] == 1).collect();
        let reach: IntLinearExp = reaching
            .iter()
            .map(|&i| IntLinearExp::from(built[i]))
            .sum();
        // The region is covered only if some reaching site has a tower.
        m.linear(reach).ge(c).post()?;
        // A tower at a reaching site covers the region.
        for &i in &reaching {
            m.linear(built[i]).le(c).post()?;
        }
        covered.push(c);
    }

    // Maximise the total population of the covered regions.
    let total = m.new_int_decision(0..=population.iter().sum::<i64>());
    let covered_pop: IntLinearExp = covered
        .iter()
        .copied()
        .zip(population.iter().copied())
        .map(|(c, p)| c * p)
        .sum();
    m.linear(covered_pop).eq(total).post()?;

    let mut out = Out::new();
    out.put("build_tower", build_tower)
        .put("total_population_covered", total);
    out.maximise(total);
    Ok(out)
}
