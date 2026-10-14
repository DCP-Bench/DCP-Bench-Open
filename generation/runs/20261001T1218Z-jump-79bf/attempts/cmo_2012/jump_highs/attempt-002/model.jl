# CMO 2012: find positive integers a and b such that a - b is a prime p and
# a * b is a perfect square n^2, with a no smaller than min_a and as small as
# possible. All numbers are at most max_val.
using JuMP

function build(instance)
    min_a = instance["min_a"]       # a must be at least this
    max_val = instance["max_val"]   # upper limit of a, b, n and p

    # the primes below max_val (the candidate values of p)
    is_prime = trues(max_val)
    is_prime[1] = false
    for i in 2:max_val, j in 2i:i:max_val
        is_prime[j] = false
    end
    primes = [q for q in 2:max_val-1 if is_prime[q]]

    model = Model()

    # a >= min_a; b >= 1; a - b = p > 0 makes a larger than b
    @variable(model, min_a <= a <= max_val, Int)
    @variable(model, 1 <= b <= max_val, Int)
    @variable(model, 2 <= p <= max_val, Int)
    @variable(model, 1 <= n <= max_val, Int)

    # a - b = p
    @constraint(model, a - b == p)

    # p is a prime: is_p[k] = 1 when p is the k-th prime of the list
    is_p = @variable(model, [1:length(primes)], Bin)
    @constraint(model, sum(is_p) == 1)
    @constraint(model, p == sum(primes[k] * is_p[k] for k in eachindex(primes)))

    # a * b = n^2 is a product of two variables, which a linear solver cannot take. With
    # a - b = p it is the same as (a + b)^2 = (a - b)^2 + 4ab = p^2 + 4 n^2, a sum of
    # squares with no product in it. Let s = a + b. Then a = (s + p) / 2 and b = (s - p) / 2,
    # so s and p have the same parity (a and b are integer variables), and
    #   s^2 = p^2 + 4 n^2.
    # Each square is a table lookup: with is_x[v] = 1 when the variable is v, its square is
    # the sum of v^2 is_x[v].
    # s = a + b is at least min_a + 1 and at most 2 * max_val - 2 (as b = a - p <= max_val - 2).
    s_lo, s_hi = min_a + 1, 2 * max_val - 2
    # n^2 = a * b < a^2 <= max_val^2, so n < max_val.
    n_hi = max_val - 1
    @variable(model, s_lo <= s <= s_hi, Int)
    is_s = @variable(model, [s_lo:s_hi], Bin)
    is_n = @variable(model, [1:n_hi], Bin)
    @constraint(model, sum(is_s) == 1)
    @constraint(model, sum(is_n) == 1)
    @constraint(model, s == sum(v * is_s[v] for v in s_lo:s_hi))
    @constraint(model, n == sum(v * is_n[v] for v in 1:n_hi))
    @constraint(model, 2a == s + p)
    @constraint(model, 2b == s - p)
    @constraint(model, sum(v^2 * is_s[v] for v in s_lo:s_hi) ==
                       sum(primes[k]^2 * is_p[k] for k in eachindex(primes)) +
                       4 * sum(v^2 * is_n[v] for v in 1:n_hi))

    # the smallest a
    @objective(model, Min, a)
    return model, Dict("a" => a, "b" => b, "n" => n, "p" => p)
end
