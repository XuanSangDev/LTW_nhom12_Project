"""Kiểm tra quy tắc tính điểm dùng chung: trọng số cố định 10-40-50 và quy đổi thang 10 sang thang 4."""
import unittest

from app.modules.analytics import grading


class GradingRulesTest(unittest.TestCase):
    def test_fixed_weights_10_40_50(self):
        self.assertEqual((grading.WEIGHT_CC, grading.WEIGHT_GK, grading.WEIGHT_CK), (10, 40, 50))
        self.assertEqual(grading.WEIGHTS, {"cc": 10, "gk": 40, "ck": 50})
        self.assertAlmostEqual(grading.final_total(8.0, 6.0, 7.0), 0.8 + 2.4 + 3.5)      # 6.7
        self.assertAlmostEqual(grading.final_total(10, 10, 10), 10.0)
        self.assertAlmostEqual(grading.final_total(0, 0, 0), 0.0)

    def test_retake_score_is_capped_at_7(self):
        self.assertEqual(grading.recognized_score(8.8, 2), 7.0)
        self.assertEqual(grading.recognized_score(6.5, 2), 6.5)
        self.assertEqual(grading.recognized_score(8.8, 1), 8.8)
        with self.assertRaises(ValueError):
            grading.recognized_score(8.0, 0)

    def test_score_to_points_never_exceeds_scale_and_bands(self):
        cases = {10: (4.0, "A"), 8.5: (4.0, "A"), 8.49: (3.5, "B+"), 8.0: (3.5, "B+"), 7.0: (3.0, "B"),
                 6.5: (2.5, "C+"), 5.5: (2.0, "C"), 5.0: (1.5, "D+"), 4.0: (1.0, "D"), 3.9: (0.0, "F"), 0: (0.0, "F")}
        for score, expected in cases.items():
            self.assertEqual(grading.score_to_points(score), expected, score)
        for bad in (10.01, -0.1, "x", float("nan")):
            with self.assertRaises(ValueError):
                grading.score_to_points(bad)



if __name__ == "__main__":
    unittest.main()
