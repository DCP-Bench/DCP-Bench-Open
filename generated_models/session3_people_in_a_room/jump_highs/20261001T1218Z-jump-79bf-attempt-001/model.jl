# People in a room: 13 people, 4 of them male, enter a room one at a time. Order them so that
# at every moment the ratio of females to males in the room is at most 7/3.
using JuMP

function build(instance)
    # The problem is fixed; the instance carries no data.
    total_people = 13
    num_males = 4

    model = Model()

    # sequence[i] = 1 when the i-th person to enter is female, 0 when male
    @variable(model, sequence[1:total_people], Bin)

    # exactly the given number of males and females enter
    @constraint(model, sum(sequence) == total_people - num_males)

    # After each of the first total_people - 1 entries the ratio females : males is at most
    # 7/3, that is 3 * females <= 7 * males, with males = (people so far) - females.
    for i in 1:total_people-1
        females_so_far = sum(sequence[1:i])
        males_so_far = i - females_so_far
        @constraint(model, 3 * females_so_far <= 7 * males_so_far)
    end

    return model, Dict("sequence" => sequence)
end
