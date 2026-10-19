// Car sequencing (CSPLib 001). Cars of different types are produced in a sequence.
// Each car type t is produced in demand[t] copies.
// Each option station o handles at most at_most[o] cars in any per_slots[o] consecutive cars.
// The cars that require an option must not be bunched together.
// The sequence lists the car type at each position, numbered from 0.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let demand = inst.ints("demand");
    let at_most = inst.ints("at_most");
    let per_slots = inst.ints("per_slots");
    let requires = inst.matrix("requires");
    let n_types = demand.len();
    let n_opts = at_most.len();
    let len = demand.iter().sum::<i64>() as usize;

    // The car type at each position of the sequence, numbered from 0.
    let seq: Vec<View<i64>> = (0..len)
        .map(|_| m.new_int_decision(0..=(n_types as i64 - 1)))
        .collect();

    // Channel each position to one Boolean per car type: is_type[p][t] holds iff seq[p] == t.
    let mut is_type: Vec<Vec<View<bool>>> = Vec::with_capacity(len);
    for p in 0..len {
        let row: Vec<View<bool>> = (0..n_types)
            .map(|t| m.linear(seq[p]).eq(t as i64).reify())
            .collect();
        is_type.push(row);
    }

    // Each position holds exactly one car type.
    for p in 0..len {
        let one = is_type[p].iter().copied().sum::<IntLinearExp>();
        m.linear(one).eq(1).post()?;
    }

    // The sequence contains exactly demand[t] cars of each type t.
    for t in 0..n_types {
        let count = (0..len).map(|p| is_type[p][t]).sum::<IntLinearExp>();
        m.linear(count).eq(demand[t]).post()?;
    }

    // Cars requiring an option must not be bunched together: any window of
    // per_slots[o] consecutive positions holds at most at_most[o] cars that require option o.
    for o in 0..n_opts {
        let k = per_slots[o] as usize;
        let needing: Vec<usize> = (0..n_types).filter(|&t| requires[t][o] == 1).collect();
        if len < k {
            continue;
        }
        for s in 0..=(len - k) {
            let window = (s..s + k)
                .flat_map(|p| needing.iter().map(move |&t| (p, t)))
                .map(|(p, t)| is_type[p][t])
                .sum::<IntLinearExp>();
            m.linear(window).le(at_most[o]).post()?;
        }

        // Implied by the demand: the sequence holds exactly the cars that require option o.
        let total: i64 = needing.iter().map(|&t| demand[t]).sum();
        let all = (0..len)
            .flat_map(|p| needing.iter().map(move |&t| (p, t)))
            .map(|(p, t)| is_type[p][t])
            .sum::<IntLinearExp>();
        m.linear(all).eq(total).post()?;
    }

    let mut out = Out::new();
    out.put("sequence", seq);
    Ok(out)
}
