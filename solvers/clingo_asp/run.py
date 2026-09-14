"""Runner protocol for the clingo_asp integration. Runs inside the image only.

A submission is an ASP program. ASP takes a logic program rather than an object
you read fields off, so the instance cannot be handed to the model the way the
Python integrations do it: this runner converts the JSON instance into facts and
grounds them alongside the submission. That conversion is the integration's
contract, so it is deliberately simple and total — index positions first, value
last — and the modelling skill documents it with the same words used here.

Declared outputs come back the same way. The request carries the reference's
output names, and each is matched to the predicate of the same name with its
first character lowered — the same rule the instance fields use, because an ASP
predicate cannot start with a capital. Index positions come first and the value
last, and this runner rebuilds the nested shape the reference expects.
"""
import json
from pathlib import Path
import signal
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish  # noqa: E402

import clingo  # noqa: E402

INPUT = Path("/input")


def predicate(key):
    """An instance field name as an ASP predicate name.

    ASP reads a leading capital as a variable, and several problems use fields
    like `N`, so the first character is lowered. A collision is refused rather
    than silently merged.
    """
    if not key or not key.replace("_", "").isalnum():
        raise ValueError(f"Instance field {key!r} is not usable as an ASP predicate name")
    return key[0].lower() + key[1:]


def term(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value)
    raise ValueError(f"Instance values must be integers, Booleans or strings; got {value!r}")


def facts(instance):
    """The instance as ground facts: name(index, ..., value)."""
    lines, names = [], {}
    for key, value in instance.items():
        name = predicate(key)
        if name in names:
            raise ValueError(f"Instance fields {names[name]!r} and {key!r} collide as {name!r}")
        names[name] = key

        def walk(current, indices):
            if isinstance(current, dict):
                raise ValueError("Nested objects in instances are not supported")
            if isinstance(current, list):
                for position, item in enumerate(current):
                    walk(item, indices + [str(position)])
            else:
                lines.append(f"{name}({','.join(indices + [term(current)])}).")

        walk(value, [])
    return "\n".join(lines)


def value_of(symbol):
    if symbol.type == clingo.SymbolType.Number:
        return symbol.number
    text = str(symbol)
    if text in ("true", "false"):
        return text == "true"
    raise ValueError(f"Declared outputs must be integers or true/false; got {text}")


def nest(entries, name):
    """Rebuild a nested list from (index tuple, value) pairs."""
    if not entries[0][0]:
        if len(entries) != 1:
            raise ValueError(f"Output {name} has several values but no index")
        return entries[0][1]
    groups = {}
    for indices, value in entries:
        groups.setdefault(indices[0], []).append((indices[1:], value))
    order = sorted(groups)
    if order != list(range(len(order))):
        raise ValueError(f"Output {name} indices must be 0-based and contiguous, got {order}")
    return [nest(groups[position], name) for position in order]


def declared_names(outputs):
    """Map each declared output key to the predicate that carries it.

    An ASP predicate cannot start with a capital, so a key like `A` is carried by
    the predicate `a`, exactly as instance fields are lowered on the way in.
    """
    wanted = {}
    for key in outputs or []:
        name = predicate(key)
        if name in wanted:
            raise ValueError(f"Declared outputs {wanted[name]!r} and {key!r} collide as {name!r}")
        wanted[name] = key
    return wanted


def outputs_of(model, wanted):
    collected = {name: [] for name in wanted}
    for symbol in model.symbols(shown=True):
        if symbol.name in collected:
            arguments = symbol.arguments
            collected[symbol.name].append(
                (tuple(a.number for a in arguments[:-1]), value_of(arguments[-1])))
    result = {}
    for name, entries in collected.items():
        key = wanted[name]
        if not entries:
            raise ValueError(f"The program shows no {name}/N atoms for declared output {key!r}")
        width = len(entries[0][0])
        if any(len(indices) != width for indices, _ in entries):
            raise ValueError(f"Output {key!r} mixes arities")
        result[key] = nest(entries, key)
    return result


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    control = clingo.Control(["0"])
    control.configuration.solve.opt_mode = "optN"
    control.add("base", [], facts(request["instance"]) + "\n" +
                (INPUT / "model.lp").read_text(encoding="utf-8"))
    control.ground([("base", [])])

    wanted = declared_names(request.get("outputs"))
    seen, count, optimizing = set(), 0, False
    with control.solve(yield_=True, async_=True) as handle:
        while count < request["solution_limit"]:
            left = deadline - time.monotonic()
            if left <= 0 or not handle.wait(left):
                handle.cancel()
                # An optimization program that never proved its optimum has not
                # answered the question, so it must not look like success.
                return finish("timeout")
            model = handle.model()
            if model is None:
                # Exhausted. For an optimization program that is only a real
                # answer once some model was proven optimal.
                return finish("complete" if count else ("timeout" if optimizing else "unsat"))
            optimizing = optimizing or bool(model.cost)
            if model.cost and not model.optimality_proven:
                handle.resume()
                continue
            values = outputs_of(model, wanted)
            key = json.dumps(values, sort_keys=True)
            if key not in seen:
                seen.add(key)
                emit({"type": "solution", "values": values})
                count += 1
            handle.resume()
    finish("limit")


def main():
    try:
        request = json.loads((INPUT / "request.json").read_text())
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by clingo_asp")

        def expired(signum, frame):
            raise TimeoutError("Runner execution budget exceeded")

        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"] + 5)
        solve(request)
    except TimeoutError:
        finish("timeout")
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))


if __name__ == "__main__":
    main()
