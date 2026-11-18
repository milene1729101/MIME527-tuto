"""Run from this folder with: python -m unittest -v"""
import unittest

from simulation import simulate


class StockpileTests(unittest.TestCase):
    def test_no_trucks(self):
        # At 8 t/h, the plant uses its 32 t of Ore 2 in four hours.
        rows = simulate(until=5.0, use_trucks=False)
        last = rows[-1]
        self.assertEqual(last.time, 5.0)
        self.assertAlmostEqual(last.produced, 80.0)
        self.assertAlmostEqual(last.ore2, 0.0)
        # The pump runs for one more hour after blending stops.
        self.assertAlmostEqual(last.ore1, 36.0)

    def test_first_delivery(self):
        rows = simulate(until=3.25)
        by_time = {row.time: row for row in rows}

        self.assertIn(2.0, by_time, "Expected a record at 2 h")
        arrival = by_time[2.0]
        self.assertIn("A:HAUL_DONE", arrival.events)
        self.assertAlmostEqual(arrival.ore2_before, 16.0)
        self.assertAlmostEqual(arrival.ore2, 16.0)
        self.assertAlmostEqual(arrival.produced, 40.0)

        self.assertIn(3.0, by_time, "Expected a record at 3 h")
        unloading = by_time[3.0]
        self.assertIn("A:UNLOAD_DONE", unloading.events)
        self.assertAlmostEqual(unloading.ore2_before, 8.0)
        self.assertAlmostEqual(unloading.ore2, 24.0)
        self.assertAlmostEqual(unloading.produced, 60.0)


if __name__ == "__main__":
    unittest.main()
