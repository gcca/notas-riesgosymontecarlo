from unittest import TestCase

from toolkit import Case


class CaseTestCase(TestCase):

    def setUp(self) -> None:
        self.c = Case.Make(base=480, boot=125, ratio=0.1)
        self.c.Relength(5)

    def test_relength(self) -> None:
        base = self.c.AsDF.base.to_list()

        for value, expected in zip(
            base,
            [125.0, 137.5, 151.25, 166.38, 183.01],
        ):
            with self.subTest(expected=expected):
                self.assertAlmostEqual(value, expected, 2)

    def test_leveling(self) -> None:
        self.c.Leveling(-0.2, 0.2)
        df = self.c.AsDF
        base = df["base"].to_list()
        sub20 = df["-20.00%"].to_list()
        sup20 = df["20.00%"].to_list()

        for record in zip(
            base,
            sub20,
            sup20,
            [125.0, 137.5, 151.25, 166.38, 183.01],
            [100.0, 110.0, 121.0, 133.1, 146.41],
            [150.0, 165.0, 181.5, 199.65, 219.62],
        ):
            values = record[:3]
            expectation = record[3:]
            with self.subTest(expectation=expectation):
                base, sub20, sup20 = values
                expected_base, expected_sub20, expected_sup20 = expectation
                self.assertAlmostEqual(base, expected_base, 2)
                self.assertAlmostEqual(sub20, expected_sub20, 2)
                self.assertAlmostEqual(sup20, expected_sup20, 2)
