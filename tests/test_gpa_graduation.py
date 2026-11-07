"""Kiểm thử mô phỏng GPA mục tiêu tốt nghiệp theo số môn."""
import unittest
from app import create_app
from app.modules.analytics import gpa_simulation
from app.modules.analytics.services import EARNED_GPA_COURSES, TOTAL_GPA_COURSES


class GraduationGpaTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_target_340_uses_remaining_course_count(self):
        result = gpa_simulation.simulate(3.40, "graduation")
        raw = (3.40 * TOTAL_GPA_COURSES - 3.12 * EARNED_GPA_COURSES) / (TOTAL_GPA_COURSES - EARNED_GPA_COURSES)
        self.assertEqual(result["courses_in_scope"], TOTAL_GPA_COURSES - EARNED_GPA_COURSES)
        self.assertAlmostEqual(result["required_gpa"], raw, places=2)

    def test_credit_count_does_not_change_gpa_requirement(self):
        original = self.app.config["TOTAL_PROGRAM_CREDITS"]
        try:
            before = gpa_simulation.simulate(3.4, "graduation")["required_gpa"]
            self.app.config["TOTAL_PROGRAM_CREDITS"] = original + 50
            after = gpa_simulation.simulate(3.4, "graduation")["required_gpa"]
            self.assertEqual(before, after)
        finally:
            self.app.config["TOTAL_PROGRAM_CREDITS"] = original


if __name__ == "__main__":
    unittest.main()
