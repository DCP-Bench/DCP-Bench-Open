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
    largest_prime = last(primes)

    model = Model()

    # a >= min_a, b >= 1, and a - b = p > 0 makes a larger than b
    @variable(model, min_a <= a <= max_val, Int)
    @variable(model, 1 <= b <= max_val, Int)
    @variable(model, 2 <= p <= max_val, Int)
    # n^2 = a * b < a^2 <= max_val^2, so n < max_val
    @variable(model, 1 <= n <= max_val, Int)

    @constraint(model, a - b == p)

    # p is a prime: is_p[k] = 1 when p is the k-th prime of the list
    is_p = @variable(model, [1:length(primes)], Bin)
    @constraint(model, sum(is_p) == 1)
    @constraint(model, p == sum(primes[k] * is_p[k] for k in eachindex(primes)))

    # a * b = n^2 is a product of two variables, which a linear solver cannot take. With
    # b = a - p it is a * (a - p) = a^2 - a * p = n^2. Writing a as a table lookup,
    # is_a[v] = 1 when a = v, gives a^2 = sum v^2 is_a[v] and a * p = sum v * (is_a[v] * p),
    # where each product of the binary is_a[v] and the integer p is linearised as ap[v].
    is_a = @variable(model, [min_a:max_val], Bin)
    @constraint(model, sum(is_a) == 1)
    @constraint(model, a == sum(v * is_a[v] for v in min_a:max_val))
    ap = @variable(model, [min_a:max_val], lower_bound = 0, upper_bound = largest_prime)
    @constraint(model, [v = min_a:max_val], ap[v] <= largest_prime * is_a[v])
    @constraint(model, [v = min_a:max_val], ap[v] <= p)
    @constraint(model, [v = min_a:max_val], ap[v] >= p - largest_prime * (1 - is_a[v]))

    # n^2 is a table lookup too: is_n[u] = 1 when n = u
    n_hi = max_val - 1
    is_n = @variable(model, [1:n_hi], Bin)
    @constraint(model, sum(is_n) == 1)
    @constraint(model, n == sum(u * is_n[u] for u in 1:n_hi))
    @constraint(model, sum(u^2 * is_n[u] for u in 1:n_hi) ==
                       sum(v^2 * is_a[v] for v in min_a:max_val) - sum(v * ap[v] for v in min_a:max_val))

    # the smallest a
    @objective(model, Min, a)
    return model, Dict("a" => a, "b" => b, "n" => n, "p" => p)
end
