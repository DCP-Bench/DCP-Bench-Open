# Fractions: find distinct non-zero digits A, B, C, D, E, F, G, H, I such that
# A / BC + D / EF + G / HI = 1, where BC, EF and HI are the two-digit numbers made of the
# digits B C, E F and H I.
using JuMP

function build(instance)
    # The problem is fixed; the instance carries no data.
    n = 9   # nine digits, each of 1..9, each used once

    model = Model()

    # is_digit[i, v] = 1 when letter i (A, B, C, D, E, F, G, H, I = 1..9) is the digit v. Each
    # letter has one digit and each digit is used by one letter (all different).
    @variable(model, is_digit[1:n, 1:n], Bin)
    @constraint(model, [i = 1:n], sum(is_digit[i, :]) == 1)
    @constraint(model, [v = 1:n], sum(is_digit[:, v]) == 1)

    # x[i] = the digit of letter i, the declared outputs, tied to the indicators
    @variable(model, 1 <= x[1:n] <= n, Int)
    @constraint(model, [i = 1:n], x[i] == sum(v * is_digit[i, v] for v in 1:n))
    A, B, C, D, E, F, G, H, I = 1, 2, 3, 4, 5, 6, 7, 8, 9   # position of each letter

    # the three two-digit denominators, each between 11 and 99
    BC = 10 * x[B] + x[C]
    EF = 10 * x[E] + x[F]
    HI = 10 * x[H] + x[I]

    # digit_times(i, y, U) = x[i] * y for a bounded quantity 0 <= y <= U: a digit times a
    # quantity is the sum over the digit's values v of v * (is_digit[i, v] * y), and each
    # binary-times-bounded product is linearised with a helper z.
    function digit_times(i, y, U)
        z = @variable(model, [1:n], lower_bound = 0, upper_bound = U)
        for v in 1:n
            @constraint(model, z[v] <= U * is_digit[i, v])
            @constraint(model, z[v] <= y)
            @constraint(model, z[v] >= y - U * (1 - is_digit[i, v]))
        end
        return sum(v * z[v] for v in 1:n)
    end

    # The equation A/BC + D/EF + G/HI = 1, multiplied by BC * EF * HI, is
    #   A * (EF * HI) + D * (BC * HI) + G * (BC * EF) = BC * (EF * HI).
    # The products of two denominators are named first (each at most 99 * 99).
    @variable(model, 0 <= EF_HI <= 99 * 99)
    @variable(model, 0 <= BC_HI <= 99 * 99)
    @variable(model, 0 <= BC_EF <= 99 * 99)
    @constraint(model, EF_HI == 10 * digit_times(E, HI, 99) + digit_times(F, HI, 99))
    @constraint(model, BC_HI == 10 * digit_times(B, HI, 99) + digit_times(C, HI, 99))
    @constraint(model, BC_EF == 10 * digit_times(B, EF, 99) + digit_times(C, EF, 99))
    @constraint(model,
                digit_times(A, EF_HI, 99 * 99) + digit_times(D, BC_HI, 99 * 99) +
                digit_times(G, BC_EF, 99 * 99) ==
                10 * digit_times(B, EF_HI, 99 * 99) + digit_times(C, EF_HI, 99 * 99))

    return model, Dict("A" => x[A], "B" => x[B], "C" => x[C], "D" => x[D], "E" => x[E],
                       "F" => x[F], "G" => x[G], "H" => x[H], "I" => x[I])
end
