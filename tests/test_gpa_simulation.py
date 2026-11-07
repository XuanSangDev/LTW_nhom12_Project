"""Kiểm thử mô phỏng GPA theo trung bình số môn, không theo trọng số tín chỉ."""
import json
import unittest

from app import create_app
from app.modules.analytics import gpa_simulation as g
from app.modules.analytics.services import EARNED_GPA_COURSES, TOTAL_GPA_COURSES, RESULTS_COURSES


class GpaSimulationTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_graduation_target_uses_course_count(self):
        r = g.simulate(3.40, "graduation")
        expected = (3.40 * TOTAL_GPA_COURSES - 3.12 * EARNED_GPA_COURSES) / (TOTAL_GPA_COURSES - EARNED_GPA_COURSES)
        self.assertEqual(r["status"], "feasible")
        self.assertEqual(r["courses_in_scope"], TOTAL_GPA_COURSES - EARNED_GPA_COURSES)
        self.assertAlmostEqual(r["required_gpa"], expected, places=2)
        self.assertNotIn("credits_in_scope", r)  # tín chỉ không làm mẫu số GPA

    def test_semester_and_graduation_scopes_are_different(self):
        semester = g.simulate(3.0, "semester")
        graduation = g.simulate(3.0, "graduation")
        self.assertEqual(semester["courses_in_scope"], len(g.CURRENT_COURSES))
        self.assertNotEqual(semester["max_reachable"], graduation["max_reachable"])

    def test_target_above_reachable_maximum_is_impossible(self):
        r = g.simulate(4.0, "graduation")
        self.assertEqual(r["status"], "impossible")
        self.assertIsNone(r["required_gpa"])
        self.assertLess(r["max_reachable"], 4.0)

    def test_achieved_when_current_gpa_already_exceeds_target_and_no_courses_remain(self):
        original = g.TOTAL_GPA_COURSES
        try:
            g.TOTAL_GPA_COURSES = g.EARNED_GPA_COURSES
            r = g.simulate(3.0, "graduation")
            self.assertEqual(r["status"], "achieved")
            self.assertEqual(r["required_gpa"], 0.0)
        finally:
            g.TOTAL_GPA_COURSES = original

    def test_semester_projection_is_arithmetic_mean_not_credit_weighted(self):
        submitted = [{"code": c["code"], "final": c["final"]} for c in RESULTS_COURSES]
        result = g.simulate_semester_courses(3.0, submitted)
        expected = sum(row["points"] for row in result["courses"]) / len(result["courses"])
        self.assertAlmostEqual(result["semester_gpa"], round(expected, 2))
        self.assertEqual(result["course_count"], len(RESULTS_COURSES))

    def test_projection_rejects_missing_or_invalid_scores(self):
        submitted = [{"code": c["code"], "final": c["final"]} for c in RESULTS_COURSES]
        with self.assertRaises(ValueError):
            g.simulate_semester_courses(3.0, submitted[:-1])
        submitted[0]["final"] = 11
        with self.assertRaises(ValueError):
            g.simulate_semester_courses(3.0, submitted)

    def test_api_projection(self):
        submitted = [{"code": c["code"], "final": c["final"]} for c in RESULTS_COURSES]
        response = self.client.post("/api/analytics/semester-projection", json={"target_gpa": 3.0, "courses": submitted})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["course_count"], len(RESULTS_COURSES))


if __name__ == "__main__":
    unittest.main()
