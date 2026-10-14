# Rectangle packing: place rectangles of given widths and heights (not rotated) inside a
# larger rectangle without overlap, so that the larger rectangle has the smallest area.
using JuMP

function build(instance)
    widths = instance["widths"]
    heights = instance["heights"]
    n = length(widths)

    # The larger rectangle is at least as wide (high) as the widest (highest) item and at
    # most as wide (high) as all items side by side (stacked); these are the reference's bounds.
    min_x, max_x = maximum(widths), sum(widths)
    min_y, max_y = maximum(heights), sum(heights)

    model = Model()

    # pos_x[i], pos_y[i] = lower-left corner of item i, from 0 (declared outputs). An item
    # must lie inside the larger rectangle, so its corner is at most max - its own size.
    @variable(model, 0 <= pos_x[i = 1:n] <= max_x - widths[i], Int)
    @variable(model, 0 <= pos_y[i = 1:n] <= max_y - heights[i], Int)

    # total_x, total_y = width and height of the larger rectangle (declared outputs)
    @variable(model, min_x <= total_x <= max_x, Int)
    @variable(model, min_y <= total_y <= max_y, Int)

    # Every item lies inside the larger rectangle
    @constraint(model, [i = 1:n], pos_x[i] + widths[i] <= total_x)
    @constraint(model, [i = 1:n], pos_y[i] + heights[i] <= total_y)

    # No overlap: for every two items, one lies completely left of, right of, below or above
    # the other. apart[1..4] select which of the four holds; a big-M equal to the size of the
    # largest possible rectangle (max_x or max_y) switches the other three off.
    for i in 1:n-1, j in i+1:n
        apart = @variable(model, [1:4], Bin)
        @constraint(model, pos_x[i] + widths[i] <= pos_x[j] + max_x * (1 - apart[1]))   # i left of j
        @constraint(model, pos_x[j] + widths[j] <= pos_x[i] + max_x * (1 - apart[2]))   # j left of i
        @constraint(model, pos_y[i] + heights[i] <= pos_y[j] + max_y * (1 - apart[3]))  # i below j
        @constraint(model, pos_y[j] + heights[j] <= pos_y[i] + max_y * (1 - apart[4]))  # j below i
        @constraint(model, sum(apart) >= 1)
    end

    # The area total_x * total_y is a product of two variables, which HiGHS cannot take.
    # is_width[v] = 1 when total_x = v; high_if[v] is then at least total_y (and 0 or more
    # otherwise), so area = sum of v * high_if[v] equals the product when it is minimised.
    @variable(model, is_width[min_x:max_x], Bin)
    @constraint(model, sum(is_width) == 1)
    @constraint(model, total_x == sum(v * is_width[v] for v in min_x:max_x))
    @variable(model, high_if[min_x:max_x] >= 0)
    @constraint(model, [v = min_x:max_x], high_if[v] >= total_y - max_y * (1 - is_width[v]))
    @expression(model, area, sum(v * high_if[v] for v in min_x:max_x))

    # The items cannot overlap, so the larger rectangle is at least as large as all of them
    # together (implied; it strengthens the relaxation of the area).
    @constraint(model, area >= sum(widths[i] * heights[i] for i in 1:n))

    # Minimise the area of the larger rectangle
    @objective(model, Min, area)

    return model, Dict("pos_x" => pos_x, "pos_y" => pos_y, "total_x" => total_x, "total_y" => total_y)
end
