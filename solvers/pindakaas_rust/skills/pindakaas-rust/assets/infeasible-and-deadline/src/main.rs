#![allow(dead_code, unused_imports)]
// The helper functions below are copied unchanged between the examples of this skill: each
// example is a standalone cargo project. They are the decompositions Pindakaas needs
// (all-different, element, table, min/max, reification) and the safe forms of its own calls.
use pindakaas::constraint::linear::{Comparator, LinExp, Linear, LinearEncoder};
use pindakaas::decision::integer::IntVar;
use pindakaas::solver::cadical::Cadical;
use pindakaas::solver::{SolveResult, Solver, TermSignal, TerminateCallback};
use pindakaas::{BoolVal, ClauseDatabase, ClauseDatabaseTools, Lit, Unsatisfiable, Valuation};

type Res<T = ()> = Result<T, Unsatisfiable>;

/// The default linear encoder (MixedRadix for integers, Totalizer for pseudo-Boolean).
fn enc() -> LinearEncoder {
    LinearEncoder::default()
}

/// A `BoolVal` (literal or constant) as a linear term worth 1 when true.
fn bx(b: BoolVal) -> LinExp {
    match b {
        BoolVal::Lit(l) => LinExp::from(l),
        BoolVal::Const(c) => LinExp::from(c),
    }
}

/// An integer variable as a linear term.
fn iv(x: &IntVar) -> LinExp {
    LinExp::from(x.clone())
}

/// `c * x` as a linear term; empty when `c` is 0. A zero coefficient on an integer
/// term panics inside Pindakaas ("attempt to divide by zero").
fn scaled(x: &IntVar, c: i64) -> LinExp {
    if c == 0 { LinExp::default() } else { x.clone() * c }
}

/// Posts `expr <cmp> k`.
///
/// Panics when the coefficients times the variable ranges can reach 2^62: Pindakaas
/// overflows `i64` silently there and drops or accepts constraints it should not.
fn post(s: &mut Cadical, e: LinExp, cmp: Comparator, k: i64) -> Res {
    let mut n = LinExp::default();
    n += e;
    let mut reach: i128 = (k as i128).abs();
    for (x, c) in n.int_terms() {
        let top = (x.min() as i128).abs().max((x.max() as i128).abs());
        reach += (c as i128).abs() * top;
    }
    for (_, c) in n.bool_terms() {
        reach += (c as i128).abs();
    }
    assert!(
        reach < (1i128 << 62),
        "linear constraint too wide: coefficients times ranges reach {reach}, over 2^62"
    );
    s.encode(&Linear::new(n, cmp, k), &enc())
}

/// A fresh integer variable `z` with `z == e`, its domain the bounds of `e`. `e` must
/// carry no additive constant. Use it to put an expression behind order or equality
/// literals (`z.at_most(s, k)`, `z.equals(s, k)`).
fn define(s: &mut Cadical, e: LinExp) -> Res<IntVar> {
    let mut n = LinExp::default();
    n += e;
    let (mut lo, mut hi) = (0i64, 0i64);
    for (x, c) in n.int_terms() {
        let (a, b) = (c * x.min(), c * x.max());
        lo += a.min(b);
        hi += a.max(b);
    }
    for (_, c) in n.bool_terms() {
        lo += c.min(0);
        hi += c.max(0);
    }
    let z = IntVar::new(lo..=hi);
    post(s, n - iv(&z), Comparator::Equal, 0)?;
    Ok(z)
}

/// A literal for a `BoolVal`: a constant becomes a fresh literal fixed to that value.
fn lit_of(s: &mut Cadical, b: BoolVal) -> Res<Lit> {
    match b {
        BoolVal::Lit(l) => Ok(l),
        BoolVal::Const(c) => {
            let l = s.new_lit();
            s.add_clause([if c { l } else { !l }])?;
            Ok(l)
        }
    }
}

/// `conds -> expr <cmp> k`, in the form that is safe over integer terms.
///
/// Pindakaas's own `encode_implied` narrows the domains of the integer variables for
/// good, so a false condition still removes values (silent wrong answers). Here the sum
/// is defined unconditionally as `z`, and only `z`'s order literals sit behind the
/// conditions.
fn post_if(s: &mut Cadical, conds: &[Lit], e: LinExp, cmp: Comparator, k: i64) -> Res {
    let z = define(s, e)?;
    let neg: Vec<BoolVal> = conds.iter().map(|&c| BoolVal::Lit(!c)).collect();
    if cmp != Comparator::GreaterEq {
        let l = z.at_most(s, k)?;
        s.add_clause(neg.iter().copied().chain([l]))?;
    }
    if cmp != Comparator::LessEq {
        let l = z.at_least(s, k)?;
        s.add_clause(neg.iter().copied().chain([l]))?;
    }
    Ok(())
}

/// A literal `b` with `b <-> expr <= k`.
fn reify_le(s: &mut Cadical, e: LinExp, k: i64) -> Res<Lit> {
    let z = define(s, e)?;
    let l = z.at_most(s, k)?;
    lit_of(s, l)
}

/// A literal `b` with `b <-> expr == k`.
fn reify_eq(s: &mut Cadical, e: LinExp, k: i64) -> Res<Lit> {
    let z = define(s, e)?;
    let l = z.equals(s, k)?;
    lit_of(s, l)
}

/// All-different: at most one variable takes each value.
fn all_different(s: &mut Cadical, xs: &[IntVar]) -> Res {
    let lo = xs.iter().map(|x| x.min()).min().expect("all_different of nothing");
    let hi = xs.iter().map(|x| x.max()).max().expect("all_different of nothing");
    for v in lo..=hi {
        let mut e = LinExp::default();
        let mut n = 0;
        for x in xs {
            let b = x.equals(s, v)?;
            if b != BoolVal::Const(false) {
                e += bx(b);
                n += 1;
            }
        }
        if n > 1 {
            post(s, e, Comparator::LessEq, 1)?;
        }
    }
    Ok(())
}

/// `c == the number of xs equal to v`.
fn count_eq(s: &mut Cadical, xs: &[IntVar], v: i64, c: &IntVar) -> Res {
    let mut e = LinExp::default();
    for x in xs {
        e += bx(x.equals(s, v)?);
    }
    post(s, e - iv(c), Comparator::Equal, 0)
}

/// `r == arr[idx]`, 0-based; `idx` is restricted to the array.
fn element_const(s: &mut Cadical, idx: &IntVar, arr: &[i64], r: &IntVar) -> Res {
    post(s, iv(idx), Comparator::GreaterEq, 0)?;
    post(s, iv(idx), Comparator::LessEq, arr.len() as i64 - 1)?;
    for (j, &a) in arr.iter().enumerate() {
        let ij = idx.equals(s, j as i64)?;
        let ra = r.equals(s, a)?;
        s.add_clause([!ij, ra])?;
    }
    Ok(())
}

/// `r == xs[idx]` over variables, 0-based; `idx` is restricted to the array.
fn element_var(s: &mut Cadical, idx: &IntVar, xs: &[IntVar], r: &IntVar) -> Res {
    post(s, iv(idx), Comparator::GreaterEq, 0)?;
    post(s, iv(idx), Comparator::LessEq, xs.len() as i64 - 1)?;
    for (j, x) in xs.iter().enumerate() {
        match idx.equals(s, j as i64)? {
            BoolVal::Lit(l) => post_if(s, &[l], iv(x) - iv(r), Comparator::Equal, 0)?,
            BoolVal::Const(true) => post(s, iv(x) - iv(r), Comparator::Equal, 0)?,
            BoolVal::Const(false) => {}
        }
    }
    Ok(())
}

/// Positive table: `xs` takes the values of one of `rows`.
fn table(s: &mut Cadical, xs: &[IntVar], rows: &[Vec<i64>]) -> Res {
    let mut pick = LinExp::default();
    for row in rows {
        let t = s.new_lit();
        pick += LinExp::from(t);
        for (x, &v) in xs.iter().zip(row) {
            let e = x.equals(s, v)?;
            s.add_clause([BoolVal::Lit(!t), e])?;
        }
    }
    post(s, pick, Comparator::Equal, 1)
}

/// `m == min(xs)`.
fn minimum(s: &mut Cadical, xs: &[IntVar], m: &IntVar) -> Res {
    for x in xs {
        post(s, iv(m) - iv(x), Comparator::LessEq, 0)?;
    }
    for v in (m.min() + 1)..=m.max() {
        let mut cl = vec![m.at_least(s, v)?];
        for x in xs {
            cl.push(!x.at_least(s, v)?);
        }
        s.add_clause(cl)?;
    }
    Ok(())
}

/// `m == max(xs)`.
fn maximum(s: &mut Cadical, xs: &[IntVar], m: &IntVar) -> Res {
    for x in xs {
        post(s, iv(m) - iv(x), Comparator::GreaterEq, 0)?;
    }
    for v in m.min()..m.max() {
        let mut cl = vec![m.at_most(s, v)?];
        for x in xs {
            cl.push(!x.at_most(s, v)?);
        }
        s.add_clause(cl)?;
    }
    Ok(())
}

/// `z == x * y`, by cases on the values of `x` (give `x` the smaller domain).
fn times(s: &mut Cadical, x: &IntVar, y: &IntVar, z: &IntVar) -> Res {
    let vals: Vec<i64> = x.domain().iter().flatten().collect();
    for a in vals {
        match x.equals(s, a)? {
            BoolVal::Lit(l) => post_if(s, &[l], scaled(y, a) - iv(z), Comparator::Equal, 0)?,
            BoolVal::Const(true) => post(s, scaled(y, a) - iv(z), Comparator::Equal, 0)?,
            BoolVal::Const(false) => {}
        }
    }
    Ok(())
}

/// `r == x mod k` for `x >= 0` and a constant `k > 0`: `x == q*k + r` with `0 <= r < k`.
fn mod_const(s: &mut Cadical, x: &IntVar, k: i64, r: &IntVar) -> Res {
    let q = IntVar::new(0..=(x.max() / k));
    post(s, iv(r), Comparator::LessEq, k - 1)?;
    post(s, iv(r), Comparator::GreaterEq, 0)?;
    post(s, iv(&q) * k + iv(r) - iv(x), Comparator::Equal, 0)
}

/// `a == |x|`.
fn abs_eq(s: &mut Cadical, x: &IntVar, a: &IntVar) -> Res {
    let neg = x.at_most(s, -1)?;
    let neg = lit_of(s, neg)?;
    post_if(s, &[neg], iv(a) + iv(x), Comparator::Equal, 0)?;
    post_if(s, &[!neg], iv(a) - iv(x), Comparator::Equal, 0)
}

/// Every output integer needs at least one view before the first solve, or `value()` returns
/// the domain minimum without looking at the model.
fn touch(s: &mut Cadical, x: &IntVar) -> Res {
    if x.card() > 1 {
        let _ = x.equals(s, x.min())?;
    }
    Ok(())
}

/// Up to `cap` solutions projected on `vars`, found one at a time with a blocking clause
/// over the projection. `None` means the search was interrupted.
fn all_solutions(s: &mut Cadical, vars: &[IntVar], cap: usize) -> Res<Option<Vec<Vec<i64>>>> {
    for x in vars {
        touch(s, x)?;
    }
    let mut out = Vec::new();
    while out.len() < cap {
        // Read the values first: the solution borrows the solver.
        let row: Option<Vec<i64>> = match s.solve() {
            SolveResult::Satisfied(sol) => Some(vars.iter().map(|x| x.value(&sol)).collect()),
            SolveResult::Unsatisfiable(_) => None,
            SolveResult::Unknown => return Ok(None),
        };
        let Some(row) = row else { break };
        let mut block = Vec::new();
        for (x, &v) in vars.iter().zip(&row) {
            block.push(!x.equals(s, v)?);
        }
        out.push(row);
        if s.add_clause(block).is_err() {
            break; // the blocking clause is empty: that was the last solution
        }
    }
    Ok(Some(out))
}

use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::{Duration, Instant};

// Three ways a model comes back empty, and how to stop a long search.
fn main() {
    // 1. A contradiction that encoding detects: the call returns Err(Unsatisfiable).
    let mut s = Cadical::default();
    let x = IntVar::new(0..=3);
    let detected = post(&mut s, iv(&x), Comparator::GreaterEq, 7);
    println!("x >= 7 over 0..=3 while encoding: {:?}", detected.is_err());
    assert!(detected.is_err());

    // 2. A contradiction only search finds: encoding succeeds, solve() says Unsatisfiable.
    let mut s = Cadical::default();
    let x: Vec<IntVar> = (0..3).map(|_| IntVar::new(0..=1)).collect();
    all_different(&mut s, &x).unwrap(); // pigeonhole
    let rows = all_solutions(&mut s, &x, 1).unwrap().expect("not interrupted");
    println!("3 different values in 0..=1: {} rows", rows.len());
    assert!(rows.is_empty());

    // 3. A deadline: the terminate callback is polled during search and makes solve()
    // return Unknown. Encoding is not interruptible and runs to the end first.
    let mut s = Cadical::default();
    let n = 11;
    let marks: Vec<IntVar> = (0..n).map(|_| IntVar::new(0..=71)).collect();
    post(&mut s, iv(&marks[0]), Comparator::Equal, 0).unwrap();
    for i in 0..n - 1 {
        post(&mut s, iv(&marks[i + 1]) - iv(&marks[i]), Comparator::GreaterEq, 1).unwrap();
    }
    let mut diffs = Vec::new();
    for i in 0..n {
        for j in (i + 1)..n {
            diffs.push(define(&mut s, iv(&marks[j]) - iv(&marks[i])).unwrap());
        }
    }
    all_different(&mut s, &diffs).unwrap();
    let deadline = Instant::now() + Duration::from_secs(2);
    let stop = Arc::new(AtomicBool::new(false));
    let flag = stop.clone();
    s.set_terminate_callback(Some(move || {
        if flag.load(Ordering::Relaxed) || Instant::now() >= deadline {
            TermSignal::Terminate
        } else {
            TermSignal::Continue
        }
    }));
    let started = Instant::now();
    let result = all_solutions(&mut s, &marks, 1).unwrap();
    println!("11-mark Golomb ruler within 71: interrupted = {} after {:?}", result.is_none(), started.elapsed());
    assert!(result.is_none());
}
