// Three sum: given a collection of integers, find a number of elements that sum to zero.
// Output: indices, a list of booleans, one per element, true when the element is selected.
// The number of selected elements is m (instance field).

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let nums = inst.ints("nums");
    let m = inst.int("m");
    let n = nums.len();

    let mut bs: Vec<Lit> = Vec::with_capacity(n);
    for _ in 0..n {
        bs.push(s.new_lit());
    }

    // a number of elements are selected: exactly m of them
    let mut count = LinExp::default();
    for b in &bs {
        count += LinExp::from(b.clone());
    }
    post(s, count, Comparator::Equal, m)?;

    // the selected elements sum to zero
    let mut total = LinExp::default();
    for (b, c) in bs.iter().zip(nums.iter()) {
        total += b.clone() * *c;
    }
    post(s, total, Comparator::Equal, 0)?;

    let mut out = Out::new();
    out.put("indices", &bs);
    Ok(out)
}
