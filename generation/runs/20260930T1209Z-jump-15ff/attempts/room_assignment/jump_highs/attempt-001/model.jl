# Room assignment: give every booking (a room from a start date up to, but not
# including, an end date) one room for its whole stay, so that no room hosts two
# bookings on the same night. Some bookings have their room fixed already.
using JuMP
using Dates

function build(instance)
    rooms = instance["max_rooms"]
    starts = Date.(instance["start_data"])
    ends = Date.(instance["end_data"])
    preassigned = instance["preassigned_room_data"]   # -1 when the room is not fixed
    n = length(starts)
    model = Model()
    # in_room[i, r] = 1 when booking i gets room r - 1
    @variable(model, in_room[1:n, 1:rooms], Bin)
    @constraint(model, [i = 1:n], sum(in_room[i, :]) == 1)
    for i in 1:n
        preassigned[i] != -1 && fix(in_room[i, preassigned[i] + 1], 1; force = true)
    end
    # two bookings that share a night never share a room
    for i in 1:n-1, j in i+1:n
        if max(starts[i], starts[j]) < min(ends[i], ends[j])
            @constraint(model, [r = 1:rooms], in_room[i, r] + in_room[j, r] <= 1)
        end
    end
    @variable(model, 0 <= room[1:n] <= rooms - 1, Int)
    @constraint(model, [i = 1:n], room[i] == sum((r - 1) * in_room[i, r] for r in 1:rooms))
    return model, Dict("room_assignments" => room)
end
