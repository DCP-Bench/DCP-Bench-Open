// Dudeney numbers: a positive integer that is a perfect cube, such that the sum
// of its digits equals the cube root of the number. Print such a number (number)
// that is also larger than 1. The number has at most n digits (n from the instance).

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    let maxv: i64 = 10i64.pow(n as u32) - 1;

    // Largest cube root m with m^3 <= maxv; m is at least 2 so that the number exceeds 1.
    let mut kmax: i64 = 2;
    while (kmax + 1) * (kmax + 1) * (kmax + 1) <= maxv {
        kmax += 1;
    }

    // The cube root m = idx + 2, with idx a 0-based index into the cubes table.
    let idx = IntVar::new(0..=kmax - 2);
    let m = IntVar::new(2..=kmax);
    post(s, iv(&idx) + scaled(&m, -1), Comparator::Equal, -2)?;

    // The number is a perfect cube: number = m^3, read from the table of cubes 2^3..kmax^3.
    let cubes: Vec<i64> = (2..=kmax).map(|j| j * j * j).collect();
    // The domain holds only the cube values: a dense range of up to 10^n values exhausts memory.
    let number = IntVar::new(pindakaas::RangeList::from_iter(cubes.iter().map(|&c| c..=c)));
    element_const(s, &idx, &cubes, &number)?;

    // The number has n decimal digits: number = sum of digit_i * 10^i.
    let digits: Vec<IntVar> = (0..n).map(|_| IntVar::new(0..=9)).collect();
    let mut value = LinExp::default();
    let mut digit_sum = LinExp::default();
    let mut place: i64 = 1;
    for d in &digits {
        value += scaled(d, place);
        digit_sum += iv(d);
        place *= 10;
    }
    value += scaled(&number, -1);
    post(s, value, Comparator::Equal, 0)?;

    // the sum of its digits is equal to the cube root of the number
    digit_sum += scaled(&m, -1);
    post(s, digit_sum, Comparator::Equal, 0)?;

    let mut out = Out::new();
    out.put("number", &number);
    Ok(out)
}
