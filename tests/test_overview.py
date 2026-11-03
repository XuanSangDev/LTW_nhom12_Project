import json
import unittest

from app import create_app


class OverviewPageTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_overview_renders_with_data(self):
        r = self.client.get("/phan-tich/tong-quan")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        for text in ["Tổng quan học tập", "3.12", "3.25", "78", "/ 130 tín", "Hoàn thành 60%", "Còn lại 52 tín",
                     "6 môn", "18 tín chỉ", "Tuần thứ 9 / 16", "Xếp loại: Khá", "43.6%", "Cơ sở dữ liệu", "Kinh tế vi mô"]:
            self.assertIn(text, html, text)

    def test_sidebar_single_active_item_per_page(self):
        pages = {"tong-quan": "Tổng quan học tập", "ket-qua": "Kết quả học tập", "tien-do": "Tiến độ chương trình",
                 "hoat-dong": "Hoạt động học tập", "canh-bao": "Cảnh báo sớm", "muc-tieu": "Mục tiêu & mô phỏng GPA"}
        for path, label in pages.items():
            r = self.client.get(f"/phan-tich/{path}")
            self.assertEqual(r.status_code, 200, path)
            html = r.get_data(as_text=True)
            self.assertEqual(html.count('aria-current="page"'), 1, path)
            # mục đang sáng đúng là trang hiện tại
            active_block = html.split('aria-current="page"')[1].split("</a>")[0]
            self.assertIn(label.replace("&", "&amp;"), active_block, path)

    def test_removed_features_and_invented_data_are_gone(self):
        html = self.client.get("/phan-tich/tong-quan").get_data(as_text=True)
        for text in ["Báo cáo học tập", "Kế hoạch gợi ý", "Xuất báo cáo", "hungtq@", "Trần Quang Hưng",
                     "Phòng 402", "Học bổng", "Dự báo mô phỏng", "Lịch học", "googleusercontent"]:
            self.assertNotIn(text, html, text)

    def test_notification_badge_from_data_and_single_footer(self):
        html = self.client.get("/phan-tich/tong-quan").get_data(as_text=True)
        self.assertIn(">2</span>", html)
        self.assertEqual(html.count("Dữ liệu minh họa phục vụ mục đích học tập."), 1)

    def test_api_overview_same_service(self):
        r = self.client.get("/api/analytics/overview")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(data["kpi"]["earned_credits"], 78)
        self.assertEqual(data["kpi"]["remaining_credits"], 52)
        self.assertEqual(len(data["gpa_chart"]["points"]), 5)

    def test_results_page_renders_with_mock_data(self):
        r = self.client.get("/phan-tich/ket-qua")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        for text in ["Kết quả học tập", "Điểm tổng kết theo môn", "Chi tiết điểm học phần",
                     "Lập trình Web", "Cơ sở dữ liệu", "GPA học kỳ", "subjectSearch"]:
            self.assertIn(text, html, text)

    def test_root_redirects(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 302)


if __name__ == "__main__":
    unittest.main()
