"""Two Ore 2 routes with a shared loader."""
from bisect import insort
from dataclasses import dataclass
from itertools import count
from math import inf
from drs import EPS


@dataclass(frozen=True)
class Truck:
    payload: float
    first_at_loader: float = 0.0
    load_h: float = 1.0
    haul_h: float = 1.0
    unload_h: float = 1.0
    return_h: float = 1.0
    muckpile: str = "Loading area"


class Haulage:
    """Keep the truck schedule and the loader queue."""

    def __init__(self, trucks):
        self.trucks = trucks
        self.loader = None  # Name of the truck being loaded, or None if idle.
        self.waiting = []
        self.order = count()  # At equal times, handle events in insertion order.
        self.fel = []
        for name, truck in trucks.items():
            self.schedule(truck.first_at_loader, "AT_LOADER", name)

    def schedule(self, time, event, name):
        # Returns go to the truck's source.
        location = "Blend" if event in ("HAUL_DONE", "UNLOAD_DONE") else self.trucks[name].muckpile
        insort(self.fel, (time, next(self.order), event, name, location))

    def calendar(self):
        items = [f"{time:g} {name}:{event}@{location}"
                 for time, _, event, name, location in self.fel]
        return "[" + " | ".join(items) + "]"

    def handle_next(self, stock, trace):
        if trace:
            before = self.calendar()
        time, _, event, name, location = self.fel[0]
        del self.fel[0]
        truck = self.trucks[name]

        if event in ("AT_LOADER", "RETURN_DONE"):
            self.waiting.append(name)
            action = f"{name} is at {location} and joins the shared loader queue"
        elif event == "LOAD_DONE":
            assert self.loader == name
            self.loader = None
            self.schedule(time + truck.haul_h, "HAUL_DONE", name)
            action = f"{name} releases the loader at {location} and hauls Ore 2 to Blend"
        elif event == "HAUL_DONE":
            self.schedule(time + truck.unload_h, "UNLOAD_DONE", name)
            action = f"{name} arrives at Blend from {truck.muckpile} and starts unloading"
        elif event == "UNLOAD_DONE":
            stock[1] += truck.payload  # The only place a truck adds Ore 2.
            self.schedule(time + truck.return_h, "RETURN_DONE", name)
            action = f"{name} deposits {truck.payload:g} t of Ore 2 at Blend and returns to {truck.muckpile}"
        else:
            raise ValueError(f"Unknown truck event: {event}")

        # Give the free loader to the truck that has waited longest.
        if self.loader is None and self.waiting:
            self.loader = self.waiting[0]
            del self.waiting[0]
            self.schedule(time + self.trucks[self.loader].load_h, "LOAD_DONE", self.loader)
            action += f"; {self.loader} starts loading at {self.trucks[self.loader].muckpile}"

        if trace:
            print(f"  {name}:{event}@{location} at {time:g} h")
            print(f"    FEL before: {before}")
            print(f"    Action:     {action}")
            print(f"    FEL after:  {self.calendar()}")
            print(f"    Loader: {self.loader or 'idle'}; waiting: {self.waiting}")
        return f"{name}:{event}"

    def next_time(self):
        """Read the next truck time without removing the event."""
        return self.fel[0][0] if self.fel else inf

    def handle_due(self, now, stock, until, trace=False):
        """At the current clock time, execute all due truck events in order."""
        labels = []
        while self.fel and self.fel[0][0] <= now + EPS and self.fel[0][0] < until:
            if self.fel[0][0] < now - EPS:
                raise RuntimeError("A pending truck event was skipped; check the clock selection.")
            labels.append(self.handle_next(stock, trace))
        return labels


def make_fleet(use_trucks=True):
    trucks = {
        "A": Truck(payload=16.0, muckpile="North", haul_h=1.0, return_h=1.0),
        "B": Truck(payload=12.0, muckpile="South", haul_h=1.5, return_h=1.5),
    } if use_trucks else {}
    return Haulage(trucks)
