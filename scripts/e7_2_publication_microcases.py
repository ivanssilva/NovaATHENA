"""E7.2 piloto: validação funcional com eventos sintéticos, sem modelo temporal."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Instruction:
    slot: int
    generation: int


@dataclass(frozen=True)
class Region:
    name: str
    members: tuple[Instruction, ...]
    guards: tuple[str, ...] = ()


def publication_log(regions, events, speculative, *, validate_commit=True):
    """Return (event index, region name) for the first publication of each region."""
    active = {}
    latest_generation = {}
    dispatched, committed, killed = set(), set(), set()
    resolved, failed = set(), set()
    formed, published = set(), set()
    log = []

    for index, (event, value) in enumerate(events, start=1):
        if event == "dispatch":
            assert value.slot not in active
            assert value.generation > latest_generation.get(value.slot, -1)
            latest_generation[value.slot] = value.generation
            active[value.slot] = value
            dispatched.add(value)
        elif event == "commit":
            if active.get(value.slot) == value:
                del active[value.slot]
                committed.add(value)
        elif event == "squash":
            guard, victims = value
            failed.add(guard)
            for victim in victims:
                assert active.get(victim.slot) == victim
                del active[victim.slot]
                killed.add(victim)
        elif event == "resolve":
            resolved.add(value)
        elif event == "flush":
            killed.update(active.values())
            active.clear()
        else:
            raise ValueError(event)

        available = dispatched if speculative else committed
        for region in regions:
            if killed.intersection(region.members) or failed.intersection(region.guards):
                formed.discard(region.name)
                continue
            if set(region.members) <= available:
                formed.add(region.name)
            ready = set(region.members) <= committed and set(region.guards) <= resolved
            if region.name in formed and region.name not in published and (ready or not validate_commit):
                log.append((index, region.name))
                published.add(region.name)
    return log


def main():
    a, b, c = Instruction(0, 1), Instruction(1, 1), Instruction(1, 2)
    d = Instruction(0, 2)
    cases = [
        ("commit parcial", [Region("R", (a, b))],
         [("dispatch", a), ("dispatch", b), ("commit", a), ("commit", b)], [(4, "R")]),
        ("desvio correto", [Region("R", (a,), ("B1",))],
         [("dispatch", a), ("resolve", "B1"), ("commit", a)], [(3, "R")]),
        ("caminho errado com recuperação", [Region("errada", (a, b), ("B1",)), Region("correta", (a, c))],
         [("dispatch", a), ("dispatch", b), ("squash", ("B1", (b,))),
          ("commit", a), ("dispatch", c), ("commit", c)], [(6, "correta")]),
        ("flush após commit parcial", [Region("R", (a, b))],
         [("dispatch", a), ("dispatch", b), ("commit", a), ("flush", None)], []),
        ("reutilização do slot e commit obsoleto", [Region("antiga", (a, b)), Region("nova", (a, c))],
         [("dispatch", a), ("dispatch", b), ("commit", a), ("flush", None),
          ("dispatch", c), ("commit", b), ("commit", c)], [(7, "nova")]),
        ("reutilização após commit normal", [Region("antiga", (a,)), Region("nova", (d,))],
         [("dispatch", a), ("commit", a), ("dispatch", d), ("commit", a), ("commit", d)],
         [(2, "antiga"), (5, "nova")]),
    ]
    detected = 0
    for name, regions, events, expected in cases:
        for speculative in (False, True):
            actual = publication_log(regions, events, speculative)
            assert actual == expected, (name, speculative, actual, expected)
        unsafe = publication_log(regions, events, True, validate_commit=False)
        detected += unsafe != expected
        print(f"{name}: {expected}")
    assert detected == len(cases)
    print(f"{len(cases)} casos, 2 políticas validadas, 0 publicações indevidas; "
          f"controle sem validação detectado em {detected}/{len(cases)} casos.")


if __name__ == "__main__":
    main()
