// Mario: Mario needs to collect as much gold as possible by visiting different houses. He starts at Mario's house and ends at
// Luigi's house. Each house has a certain amount of gold and the travel between houses consumes fuel. Mario has a
// limited amount of fuel, and he needs to plan his route to maximize the gold collected without exceeding the fuel limit.
// Print the succeeding houses for each house (s) as a list of integers, s[i] is the house succeeding to the ith house,
// s[i]=i if not part of the route. For luigi's house, the succeeding house should be Mario's house.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("nHouses");
    let last = n as i64 - 1;
    let mario = inst.int("marioHouse") as usize;
    let luigi = inst.int("luigiHouse") as usize;
    let fuel_limit = inst.int("fuelLimit");
    let gold = inst.ints("goldInHouse");
    let arc = inst.matrix("arc_fuel");

    // s[i] is the house succeeding to the ith house, s[i]=i if not part of the route.
    let next: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(0..=last)).collect();
    m.unique(next.clone()).post()?;

    // He starts at Mario's house and ends at Luigi's house. For luigi's house, the succeeding house should be Mario's house.
    // Mario's house is on the route, and the route visits each house at most once, so visiting order increases along it.
    m.linear(next[luigi]).eq(mario as i64).post()?;
    m.linear(next[mario]).ne(mario as i64).post()?;
    let pos: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(0..=last)).collect();
    m.linear(pos[mario]).eq(0).post()?;
    for i in 0..n {
        if i == luigi {
            continue;
        }
        for j in 0..n {
            if j == i || j == mario {
                continue;
            }
            let arc_on = m.linear(next[i]).eq(j as i64).reify();
            m.linear(pos[j] - pos[i]).eq(1).implied_by(arc_on).post()?;
        }
    }

    // Each house has a certain amount of gold and the travel between houses consumes fuel. A house off the route
    // (s[i]=i) collects no gold and uses no fuel.
    let mut gold_vars: Vec<View<i64>> = Vec::with_capacity(n);
    let mut fuel_vars: Vec<View<i64>> = Vec::with_capacity(n);
    let mut sum_gold: i64 = 0;
    for i in 0..n {
        let gold_row: Vec<i64> = (0..n).map(|j| if j == i { 0 } else { gold[i] }).collect();
        let fuel_row: Vec<i64> = (0..n).map(|j| if j == i { 0 } else { arc[i][j] }).collect();
        let gmax = gold[i];
        let fmax = *fuel_row.iter().max().unwrap();
        let g = m.new_int_decision(0..=gmax);
        let f = m.new_int_decision(0..=fmax);
        m.element(gold_row).index(next[i]).result(g).post()?;
        m.element(fuel_row).index(next[i]).result(f).post()?;
        sum_gold += gmax;
        gold_vars.push(g);
        fuel_vars.push(f);
    }

    // Mario has a limited amount of fuel, and he needs to plan his route without exceeding the fuel limit.
    let total_fuel: IntLinearExp = fuel_vars.iter().copied().sum();
    m.linear(total_fuel).le(fuel_limit).post()?;

    // Mario needs to collect as much gold as possible by visiting different houses.
    let total_gold: IntLinearExp = gold_vars.iter().copied().sum();
    let obj = m.new_int_decision(0..=sum_gold);
    m.linear(total_gold).eq(obj).post()?;

    let mut out = Out::new();
    out.put("s", next.clone());
    out.maximise(obj);
    Ok(out)
}
