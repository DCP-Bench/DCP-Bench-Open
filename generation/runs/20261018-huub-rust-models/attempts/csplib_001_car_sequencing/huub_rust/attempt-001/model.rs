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

    // The sequence contains exactly demand[t] cars of each type t.
    for t in 0..n_types {
        eq2(m, count_eq(&seq, t as i64), demand[t])?;
    }

    // Whether the car at each position requires option o, looked up from its type.
    let mut req: Vec<Vec<View<i64>>> = vec![Vec::new(); n_opts];
    for o in 0..n_opts {
        let col: Vec<i64> = (0..n_types).map(|t| requires[t][o]).collect();
        for p in 0..len {
            req[o].push(m.element(col.clone()).index(seq[p]).define());
        }
    }

    // Cars requiring an option must not be bunched together: any window of
    // per_slots[o] consecutive positions holds at most at_most[o] of them.
    for o in 0..n_opts {
        let k = per_slots[o] as usize;
        if len < k {
            continue;
        }
        for s in 0..=(len - k) {
            let window = req[o][s..s + k].iter().copied().sum::<IntLinearExp>();
            m.linear(window).le(at_most[o]).post()?;
        }
    }

    let mut out = Out::new();
    out.put("sequence", seq);
    Ok(out)
}
