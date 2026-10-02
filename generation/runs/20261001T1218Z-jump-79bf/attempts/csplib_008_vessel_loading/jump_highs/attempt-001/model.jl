# Vessel loading: place rectangular containers on a rectangular deck, sides parallel to
# the deck, in a single layer. Containers may not overlap, and containers of certain
# classes must be kept a minimum distance apart. Decide whether all can be positioned.
using JuMP

function build(instance)
    deck_width = instance["deck_width"]
    deck_length = instance["deck_length"]
    n = instance["n_containers"]
    width = instance["width"]           # width of each container
    length_ = instance["length"]        # length of each container
    classes = instance["classes"]       # class (1-based) of each container
    separation = instance["separation"] # minimum distance between two classes

    model = Model()

    # left[i] .. right[i] and bottom[i] .. top[i] = the space container i occupies on the
    # deck; coordinates start at 0 and stay inside the deck (declared outputs)
    @variable(model, 0 <= left[1:n] <= deck_width, Int)
    @variable(model, 0 <= right[1:n] <= deck_width, Int)
    @variable(model, 0 <= top[1:n] <= deck_length, Int)
    @variable(model, 0 <= bottom[1:n] <= deck_length, Int)

    # Each container is laid either as given (width along the deck width, length along the
    # deck length) or turned by 90 degrees. turned[i] = 1 when container i is turned.
    turned = @variable(model, [1:n], Bin)
    for i in 1:n
        @constraint(model, right[i] - left[i] == width[i] + (length_[i] - width[i]) * turned[i])
        @constraint(model, top[i] - bottom[i] == length_[i] + (width[i] - length_[i]) * turned[i])
    end

    # No overlap, and class separation: for two containers x and y, at least `sep` apart
    # (sep comes from the separation table of their classes), x is left of y, right of y,
    # below y or above y. apart[1..4] select which of the four holds; a big-M equal to the
    # largest gap the deck allows (deck size + sep) switches off the other three.
    for x in 1:n-1, y in x+1:n
        sep = separation[classes[x]][classes[y]]
        apart = @variable(model, [1:4], Bin)
        @constraint(model, right[x] + sep <= left[y] + (deck_width + sep) * (1 - apart[1]))   # x left of y
        @constraint(model, right[y] + sep <= left[x] + (deck_width + sep) * (1 - apart[2]))   # x right of y
        @constraint(model, top[x] + sep <= bottom[y] + (deck_length + sep) * (1 - apart[3]))  # x under y
        @constraint(model, top[y] + sep <= bottom[x] + (deck_length + sep) * (1 - apart[4]))  # x above y
        @constraint(model, sum(apart) >= 1)
    end

    return model, Dict("left" => left, "right" => right, "top" => top, "bottom" => bottom)
end
