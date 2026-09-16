from pychoco.model import Model


def build(instance):
    """Five floors: put Baker, Cooper, Fletcher, Miller and Smith on five
    different floors under the stated restrictions.
    """
    del instance

    model = Model()
    people = [model.intvar(1, 5, name=name) for name in "BCFMS"]
    baker, cooper, fletcher, miller, smith = people
    model.all_different(people).post()

    model.arithm(baker, "!=", 5).post()
    model.arithm(cooper, "!=", 1).post()
    model.arithm(fletcher, "!=", 5).post()
    model.arithm(fletcher, "!=", 1).post()
    model.arithm(miller, ">", cooper).post()
    # Neither Smith nor Cooper is next door to Fletcher.
    model.distance(smith, fletcher, "!=", 1).post()
    model.distance(fletcher, cooper, "!=", 1).post()

    return model, {
        "B": baker, "C": cooper, "F": fletcher, "M": miller, "S": smith,
    }
