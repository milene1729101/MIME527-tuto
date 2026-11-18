# Wednesday lab on Ore 2 deliveries

Work in pairs. Use Python 3.10 or newer and open a terminal in the folder with `simulation.py`.

## 1. Run the starter

```sh
python simulation.py --until 3.25
python -m unittest -v
```

At 3.25 h, the starter has 6 t of Ore 2 left and has made 65 t of blend. The no-truck test passes. The delivery test is skipped.

If you got the files as a ZIP, run `git init` and commit the starter files first. Use your pair number when you make a branch.

```sh
git switch -c pair-07/fel-extension
```

## 2. Write the delivery test

Predict the Ore 2 stock when A arrives and when it finishes unloading. Compare your numbers with the [0–3 h trace](reference/Ore_Blend_0_to_3h.xlsx).

| Truck A | Time (h) | Ore 2 before (t) | Ore 2 after (t) | Blend made (t) |
|---|---:|---:|---:|---:|
| Arrives at Blend | 2 | 16 | 16 | 40 |
| Finishes unloading | 3 | 8 | 24 | 60 |

In `test_simulation.py`, remove the skip and replace `self.fail(...)` with assertions. Run `python -m unittest -v`. The new test should fail because the starter has no truck records.

## 3. Connect the trucks

Fill in the two TODOs in `simulation.py`.

- In `choose_next()`, compare `T`, `fleet.next_time()` and `until`. Stop before events at `until`. Before the end time, trucks go first on a tie.
- In `run_truck_events()`, call `fleet.handle_due(now, stock, until, trace)` and return the event labels.

The stock calculations are in `drs.py`. The shared loader and both truck routes are in `haulage.py`.

## 4. Rerun and review

```sh
python -m unittest -v
python simulation.py --until 3.25 --trace
python simulation.py
python simulation.py --no-trucks
python simulation.py --ore2-start 16 --trace
```

Both tests should pass. Read the 3 h row for the unloading check. With `--until 3`, the run stops before A unloads.

| At 9 h | Ore 1 left (t) | Ore 2 left (t) | Blend made (t) |
|---|---:|---:|---:|
| No trucks | 84 | 0 | 80 |
| Trucks, 32 t of Ore 2 to start | 24 | 4 | 180 |
| Trucks, 16 t of Ore 2 to start | 42 | 0 | 150 |

Commit `simulation.py` and `test_simulation.py`. If you have a course remote, push with `git push -u origin HEAD` and open a pull request into the starter branch. For a local review, show your partner the diff and the trace.

Check that A's load is credited at 3 h. In the 16 t run, look at the two 7 h truck events before and after the 6.5 h stockout.