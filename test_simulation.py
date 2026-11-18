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

    @unittest.skip("Exercise: write the first delivery test, then remove this line.")
    def test_first_delivery(self):
        rows = simulate(until=3.25)
        # Find A:HAUL_DONE at 2 h and A:UNLOAD_DONE at 3 h in the event records.
        # At 2 h the stock stays at 16 t. At 3 h it rises from 8 t to 24 t.
        # Check that the plant has made 60 t by 3 h.
        self.fail("Replace this line with your checks for the two events.")


if __name__ == "__main__":
    unittest.main()
