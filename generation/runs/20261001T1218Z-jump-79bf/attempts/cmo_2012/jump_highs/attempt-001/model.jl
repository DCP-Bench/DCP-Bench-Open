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

    # a >= b >= 1 (as a - b = p > 0) and a >= min_a
    @variable(model, min_a <= a <= max_val, Int)
    @variable(model, 1 <= b <= max_val, Int)
    # n^2 = a * b >= 1, so n >= 1
    @variable(model, 1 <= n <= max_val, Int)
    @variable(model, 2 <= p <= max_val, Int)

    # p is a prime: is_p[k] = 1 when p is the k-th prime of the list
    is_p = @variable(model, [1:length(primes)], Bin)
    @constraint(model, sum(is_p) == 1)
    @constraint(model, p == sum(primes[k] * is_p[k] for k in eachindex(primes)))

    # a - b = p (this also gives a > b)
    @constraint(model, a - b == p)

    # a * b = n^2. The product of two variables is not linear, so b is written in
    # binary, b = sum 2^k bit[k], which makes a * b = sum 2^k (a * bit[k]); each
    # product z[k] = a * bit[k] of an integer and a binary is linearised with M = max_val.
    nbits = ndigits(max_val, base = 2)
    bit = @variable(model, [0:nbits-1], Bin)
    @constraint(model, b == sum(2^k * bit[k] for k in 0:nbits-1))
    z = @variable(model, [0:nbits-1], lower_bound = 0, upper_bound = max_val)
    @constraint(model, [k = 0:nbits-1], z[k] <= max_val * bit[k])
    @constraint(model, [k = 0:nbits-1], z[k] <= a)
    @constraint(model, [k = 0:nbits-1], z[k] >= a - max_val * (1 - bit[k]))
    # n^2 is a table lookup: is_n[u] = 1 when n = u, and then n^2 = sum u^2 is_n[u]
    is_n = @variable(model, [1:max_val], Bin)
    @constraint(model, sum(is_n) == 1)
    @constraint(model, n == sum(u * is_n[u] for u in 1:max_val))
    @constraint(model, sum(2^k * z[k] for k in 0:nbits-1) == sum(u^2 * is_n[u] for u in 1:max_val))

    # the smallest a
    @objective(model, Min, a)
    return model, Dict("a" => a, "b" => b, "n" => n, "p" => p)
end
