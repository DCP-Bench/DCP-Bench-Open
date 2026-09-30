# Kidney exchange: people donate to compatible recipients; whoever gives a kidney
# receives one, nobody gives or receives more than one, and as many transplants
# as possible take place.
using JuMP

function build(instance)
    n = instance["num_people"]
    compatible = instance["compatible"]   # compatible[i] = who i can donate to, 1-based
    model = Model()
    @variable(model, t[1:n, 1:n], Bin)
    for i in 1:n
        # whoever gives receives, and at most one each way
        @constraint(model, sum(t[i, :]) <= sum(t[:, i]))
        @constraint(model, sum(t[:, i]) <= 1)
        # only to compatible recipients
        for j in 1:n
            j in compatible[i] || fix(t[i, j], 0; force = true)
        end
    end
    @objective(model, Max, sum(t))
    return model, Dict("transplants" => t)
end
