"""Stock levels and rate columns for the DRS model."""
from dataclasses import dataclass
from math import inf
from types import MappingProxyType

EPS = 1e-9
BLEND = (0.6, 0.4)


@dataclass(frozen=True)
class RateColumn:
    """Fixed rates for one configuration, in t/h."""
    ore1_pump: float
    ore1_draw: float
    ore2_draw: float

    @property
    def net(self):
        # Ore 2 arrives in truckloads, outside this rate balance.
        return (self.ore1_pump - self.ore1_draw, -self.ore2_draw)

    @property
    def plant_draw(self):
        return self.ore1_draw + self.ore2_draw


def make_rate_columns(ore1_feed):
    """Build the rate columns for this run."""
    def at_throughput(q):
        return RateColumn(ore1_feed, BLEND[0] * q, BLEND[1] * q)

    pump_only = at_throughput(0.0)
    return MappingProxyType({
        "BLENDING":     at_throughput(20.0),
        "WAIT_ORE2":    pump_only,
        "ORE1_LIMITED": at_throughput(min(20.0, ore1_feed / BLEND[0])),
        "PAUSED":       pump_only,
    })


def select_column(stock, columns, current="BLENDING", command=None):
    """Choose the rate configuration for the interval about to start."""
    # A timed pause stays in effect through deliveries until a resume command.
    if command == "pause" or (current == "PAUSED" and command != "resume"):
        return "PAUSED"
    if stock[1] <= EPS:
        return "WAIT_ORE2"
    full = columns["BLENDING"]
    if stock[0] <= EPS and full.ore1_pump < full.ore1_draw:
        return "ORE1_LIMITED"
    return "BLENDING"


def next_tce(now, stock, net, timers):
    """DRS: predict the first stockout or timer expiry at the current rates."""
    candidates = []
    for i, (level, rate) in enumerate(zip(stock, net)):
        if level > EPS and rate < 0:
            candidates.append((now + level / -rate, f"Ore {i + 1} empty"))
    for name, remaining in timers.items():
        candidates.append((now + remaining, name))

    first = min((time for time, _ in candidates), default=inf)
    triggers = [name for time, name in candidates if abs(time - first) <= EPS]
    return first, triggers


def advance_levels(stock, timers, net, dt):
    for i, rate in enumerate(net):
        stock[i] = max(0.0, stock[i] + rate * dt)
    for name in timers:
        timers[name] = max(0.0, timers[name] - dt)


def due_timer_command(timers, events):
    command = None
    for name in ("pause", "resume"):
        if timers.get(name, inf) <= EPS:
            command = name
            del timers[name]
            events.append(f"Timer: {name}")
    return command
