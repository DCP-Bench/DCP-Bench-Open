// Session 5 grocery: a kid buys a number of items (num_items) for a total price
// (total_price, in cents). The cashier multiplied the item prices instead of adding
// them, and the product still comes to the same total price. Find the prices of the
// items (prices), in cents.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("num_items");
    let total = inst.int("total_price");

    // the prices of the items, in cents; a price cannot exceed the total, since all prices are nonnegative
    let prices = m.new_int_decisions(n, 0..=total);

    // the cashier charges a total price: adding the items gives the total price
    m.linear(prices.iter().copied().sum::<IntLinearExp>()).eq(total).post()?;

    // the cashier multiplied the items instead: the product comes to the same total price.
    // The prices are in cents, so the product is read in dollars: the product of the n prices
    // in cents, divided by 100 for each of the n - 1 factors after the first, equals the total
    // in cents. That gives product == total * 100^(n-1); the example data agrees with this reading.
    let target = total * 100i64.pow((n - 1) as u32);

    // a running product, one factor at a time; every price is at least 1 when the total is
    // positive, so each partial product is at most the target
    let mut acc = prices[0];
    for i in 1..n {
        let next = m.new_int_decision(0..=target);
        m.mul(acc, prices[i]).result(next).post()?;
        acc = next;
    }
    m.linear(acc).eq(target).post()?;

    let mut out = Out::new();
    out.put("prices", prices);
    Ok(out)
}
