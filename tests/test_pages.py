"""Kiểm tra nhanh cả 6 trang của module Phân tích học tập (chạy: python -m unittest discover -s tests -v)."""
import re
import unittest

from app import create_app

PAGES = {
    "/phan-tich/tong-quan": "Tổng quan học tập",
    "/phan-tich/ket-qua": "Kết quả học tập",
    "/phan-tich/tien-do": "Tiến độ chương trình",
    "/phan-tich/hoat-dong": "Hoạt động học tập",
    "/phan-tich/canh-bao": "Cảnh báo sớm",
    "/phan-tich/muc-tieu": "Mục tiêu &amp; mô phỏng GPA",
}
REMOVED_TEXT = [
    "Toàn bộ điểm số và thông tin tín chỉ trên trang là dữ liệu giả lập",
    "Dữ liệu minh họa phục vụ mục đích học tập",
    "Xuất báo cáo", "Xuất bảng điểm", "Xuất lộ trình", "Xuất dữ liệu", "Kế hoạch gợi ý",
    "hungtq@", "Trần Quang Hưng", "googleusercontent",
]


class AnalyticsPagesTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def html(self, url):
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200, url)
        return r.get_data(as_text=True)

    def test_every_page_has_exactly_one_active_menu_item(self):
        for url, label in PAGES.items():
            html = self.html(url)
            self.assertEqual(html.count('aria-current="page"'), 1, url)
            active = html.split('aria-current="page"')[1].split("</a>")[0]
            self.assertIn(label, active, url)

    def test_removed_text_is_gone_everywhere(self):
        for url in PAGES:
            html = self.html(url)
            for text in REMOVED_TEXT:
                self.assertNotIn(text, html, f"{url}: {text}")

    def test_every_id_used_by_inline_js_exists_in_html(self):
        for url in PAGES:
            html = self.html(url)
            js = "\n".join(
                s for s in re.findall(r"<script(?![^>]*\bsrc=)(?![^>]*application/json)[^>]*>(.*?)</script>", html, re.S)
                if "tailwind.config" not in s)
            used = set(re.findall(r"getElementById\(\s*[\"']([^\"']+)[\"']", js))
            present = set(re.findall(r'\bid="([^"]+)"', html))
            self.assertEqual(used - present, set(), url)

    def test_course_calculator_tab_and_api_are_removed(self):
        html = self.html("/phan-tich/muc-tieu")
        for removed in ["Máy tính điểm môn học", 'id="tabContent2"', 'id="calcSection"',
                        'id="calculateCourseBtn"', 'id="inputCC"', 'id="finalScoreDisplay"',
                        "/api/analytics/final-score"]:
            self.assertNotIn(removed, html, removed)

    def test_goals_page_uses_server_simulation_with_overview_credits(self):
        import json
        html = self.html("/phan-tich/muc-tieu")
        data = json.loads(re.search(r'id="goalInitial">(.*?)</script>', html, re.S).group(1))
        self.assertEqual(data["earned_credits"], 78)          # khớp trang Tổng quan (78/130)
        self.assertEqual(data["courses_after"], data["earned_gpa_courses"] + data["courses_in_scope"])
        self.assertEqual(data["remaining_gpa_courses"], data["total_gpa_courses"] - data["earned_gpa_courses"])
        self.assertIn('data-api="/api/analytics/gpa-simulation"', html)

    def test_goals_page_shows_concise_feasibility_and_keeps_semester_planner(self):
        html = self.html("/phan-tich/muc-tieu")
        self.assertIn('id="feasibilityMessage"', html)
        self.assertIn('id="maxReachableMessage"', html)
        self.assertIn('id="semesterPlanner"', html)
        self.assertIn('data-api="/api/analytics/gpa-simulation"', html)
        self.assertIn('data-api="/api/analytics/semester-projection"', html)
        self.assertLess(html.index('id="semesterTargetGpa"'), html.index('id="semesterCourseRows"'))
        self.assertNotIn("Mức GPA cần đạt ở phần học còn lại", html)
        self.assertNotIn("GPA hiện tại</span>", html)
        self.assertNotIn("GPA mục tiêu</span>", html)


    def test_alerts_read_state_is_consistent(self):
        html = self.html("/phan-tich/canh-bao")
        cards = re.findall(r"<article class=\"alert-item.*?</article>", html, re.S)
        self.assertEqual(len(cards), 3)
        for card in cards:
            unread = 'data-status="unread"' in card
            if unread:
                self.assertEqual(card.count("Đánh dấu đã đọc"), 1)
                self.assertEqual(card.count("Đã đọc"), 0)
            else:
                self.assertEqual(card.count("Đã đọc"), 1)   # chỉ một chỗ, không lặp
                self.assertIn("read-state", card)
        self.assertIn('id="bellBadge"', html)

    def test_sidebar_links_resolve(self):
        html = self.html("/phan-tich/tong-quan")
        for href in re.findall(r'href="(/phan-tich/[^"]+)"', html):
            self.assertEqual(self.client.get(href).status_code, 200, href)


if __name__ == "__main__":
    unittest.main()
