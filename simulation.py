"""Starter for the Ore 2 delivery lab."""
from argparse import ArgumentParser
from math import isfinite
from typing import NamedTuple

from drs import (EPS, advance_levels, due_timer_command, make_rate_columns,
                 next_tce, select_column)
from haulage import make_fleet


def choose_next(T, fleet, until):
    """Return (next time, reason): TCE, FEL or END."""
    # TODO 1: Include the first truck time. A truck can win a tie only before until.
    # The starter clock ignores truck events.
    if until <= T:
        return until, "END"
    return T, "TCE"


def run_truck_events(fleet, now, stock, until, trace):
    """Run the truck events due now and return their labels."""
    # TODO 2: Call the fleet handler. The clock is already at now.
    raise NotImplementedError("Connect the truck-event handler here.")


class Record(NamedTuple):
    time: float
    elapsed: float
    reason: str
    events: tuple
    ore1: float
    ore2_before: float   # After continuous draw, before events.
    ore2: float          # After events at the same time.
    produced: float
    configuration: str


def simulate(until=9.0, ore2_start=32.0, use_trucks=True, timers=None, trace=False):
    """Run from 0 h up to, but not including, events at the end time."""
    if not all(isfinite(v) and v >= 0 for v in (until, ore2_start)):
        raise ValueError("End time and starting Ore 2 stock must be non-negative.")
    timers = dict(timers or {})
    if set(timers) - {"pause", "resume"} or any(not isfinite(v) or v < 0 for v in timers.values()):
        raise ValueError("Use non-negative pause/resume countdowns.")
    stock = [24.0, ore2_start]
    columns = make_rate_columns(ore1_feed=12.0)
    RateConfiguration = select_column(stock, columns)
    fleet = make_fleet(use_trucks)
    now = produced = 0.0
    rows = [Record(now, 0, "START", (), stock[0], stock[1], stock[1], produced, RateConfiguration)]

    while now < until:
        column = columns[RateConfiguration]
        T, triggers = next_tce(now, stock, column.net, timers)
        next_time, reason = choose_next(T, fleet, until)
        if reason not in ("TCE", "FEL", "END") or not now <= next_time <= until:
            raise ValueError("Check the next time and reason in choose_next().")
        if trace:
            print(f"\n{now:g} to {next_time:g} h: {reason}. T = {T:g}; FEL = {fleet.calendar()}")

        # Apply the old column over this interval, before an unloading can add ore.
        dt = next_time - now
        advance_levels(stock, timers, column.net, dt)
        produced += column.plant_draw * dt
        now = next_time
        before = stock[1]
        events = []

        if reason == "FEL":
            events = run_truck_events(fleet, now, stock, until, trace)
            if not events:
                raise RuntimeError("A truck step must execute at least one due event.")
        elif reason == "TCE" and trace:
            print(f"  Threshold first. FEL unchanged: {fleet.calendar()}")

        if reason != "END":
            # After a tied delivery, an earlier stockout prediction may no longer apply.
            if abs(T - now) <= EPS:
                for i, level in enumerate(stock):
                    trigger = f"Ore {i + 1} empty"
                    if trigger in triggers and level <= EPS:
                        events.append("TCE: " + trigger)
            command = due_timer_command(timers, events)
            RateConfiguration = select_column(stock, columns, RateConfiguration, command)
            if dt == 0 and not events:
                raise RuntimeError("Nothing happened at this time. Check the selected branch.")

        rows.append(Record(now, dt, reason, tuple(events), stock[0], before,
                           stock[1], produced, RateConfiguration))
        if reason == "END":
            break
    return rows


if __name__ == "__main__":
    p = ArgumentParser(description="Two ore stocks feeding a 60:40 blend.")
    p.add_argument("--until", type=float, default=9.0)
    p.add_argument("--ore2-start", type=float, default=32.0)
    p.add_argument("--no-trucks", action="store_true")
    p.add_argument("--trace", action="store_true")
    args = p.parse_args()
    rows = simulate(args.until, args.ore2_start, not args.no_trucks, trace=args.trace)
    print("  h   cause     Ore 1   Ore 2 before/after   blend (t)  configuration   events")
    for r in rows:
        print(f"{r.time:4g}  {r.reason:5}  {r.ore1:8g}  {r.ore2_before:8g}/{r.ore2:<7g}"
              f"  {r.produced:9g}  {r.configuration:13}   {'; '.join(r.events)}")
