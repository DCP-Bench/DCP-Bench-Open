# Grocery: the prices of the items, in cents, add up to the total, and their
# product equals the total with the prices read in dollars, that is the total
# times 100^(items - 1). The product is stated through prime exponents: a
# product has a prime's exponent equal to the sum of its factors' exponents.
using JuMP

function exponents(value, primes)
    counts = Int[]
    for p in primes
        e = 0
        while value % p == 0
            value = div(value, p)
            e += 1
        end
        push!(counts, e)
    end
    return counts
end

function prime_factors(value)
    factors = Int[]
    p = 2
    while p * p <= value
        if value % p == 0
            push!(factors, p)
            while value % p == 0
                value = div(value, p)
            end
        end
        p += 1
    end
    value > 1 && push!(factors, value)
    return factors
end

function build(instance)
    total = instance["total_price"]
    n = instance["num_items"]
    product = total * 100^(n - 1)
    primes = prime_factors(product)
    target = exponents(product, primes)
    # a price divides the product, so it is one of its divisors up to the total
    divisors = [d for d in 1:total if product % d == 0]
    model = Model()
    @variable(model, is[1:n, 1:length(divisors)], Bin)
    @constraint(model, [i = 1:n], sum(is[i, :]) == 1)
    @variable(model, 1 <= prices[1:n] <= total, Int)
    @constraint(model, [i = 1:n], prices[i] == sum(divisors[k] * is[i, k] for k in 1:length(divisors)))
    @constraint(model, sum(prices) == total)
    # the product, prime by prime
    power = [exponents(d, primes) for d in divisors]
    @constraint(model, [q = 1:length(primes)],
                sum(power[k][q] * is[i, k] for i in 1:n, k in 1:length(divisors)) == target[q])
    return model, Dict("prices" => prices)
end
