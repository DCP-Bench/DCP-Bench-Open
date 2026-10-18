// Three-sum: given a collection of integers, select a number of elements
// (m of them) that sum to zero. Output: whether each element is selected.
fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let nums = inst.ints("nums");
    let k = inst.int("m");
    let n = nums.len();

    // Each element is selected (1) or not (0).
    let x: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(0..=1)).collect();

    // Exactly m elements are selected.
    // The number of selected elements is m.
    m.linear(x.iter().copied().sum::<IntLinearExp>()).eq(k).post()?;

    // The selected elements sum to zero.
    // The sum of the selected elements is zero.
    let weighted = x
        .iter()
        .zip(nums.iter())
        .map(|(xi, &a)| *xi * a)
        .sum::<IntLinearExp>();
    m.linear(weighted).eq(0).post()?;

    let indices: Vec<View<bool>> = x.iter().map(|xi| xi.eq(1)).collect();
    let mut out = Out::new();
    out.put("indices", indices);
    Ok(out)
}
