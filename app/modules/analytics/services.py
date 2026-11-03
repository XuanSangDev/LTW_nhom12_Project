"""Logic của trang Tổng quan học tập.

Hiện dùng DỮ LIỆU MÔ PHỎNG viết cứng (do nhóm tự đặt, không phải số liệu thật của trường).
Khi có CSDL: chỉ thay phần "DỮ LIỆU MẪU" bằng truy vấn; các hàm tính toán bên dưới giữ nguyên.
"""
import math
from flask import current_app

from app.shared import current_student

# ---------------- Tham số do nhóm tự quy định ----------------
# Ngưỡng xếp loại theo thang 4: (điểm tối thiểu, tên xếp loại).
# LƯU Ý: nhóm tự đặt để minh họa, cần đối chiếu quy chế đào tạo của trường trước khi chốt.
CLASSIFICATION = [(3.6, "Xuất sắc"), (3.2, "Giỏi"), (2.5, "Khá"), (2.0, "Trung bình")]

# ---------------- DỮ LIỆU MẪU (mô phỏng) ----------------
CUMULATIVE_GPA = 3.12
EARNED_CREDITS = 78
GPA_TARGET =  3.40
GPA_BY_TERM = [  # 5 học kỳ đã hoàn thành
    ("HK1 24-25", 2.80),
    ("HK2 24-25", 2.95),
    ("HK Hè 25", 3.05),
    ("HK1 25-26", 3.20),
    ("HK2 25-26", 3.25),
]
BEST_COURSE = {"name": "Lập trình Java", "letter": "A+", "points": 4.0}
A_GRADE_CREDITS = 34  # số tín chỉ đạt loại A/A+ trong số tín chỉ đã tích lũy

# status: good | warning | normal
CURRENT_COURSES = [
    {"code": "ITEC1120", "name": "Lập trình Web", "credits": 3, "status": "good", "note": "Giữa kỳ: 8.5/10"},
    {"code": "ITEC1125", "name": "Cơ sở dữ liệu", "credits": 3, "status": "warning", "note": "Giữa kỳ: 5.5/10 • Cần ôn tập"},
    {"code": "ITEC2105", "name": "Phân tích thiết kế hệ thống", "credits": 3, "status": "good", "note": "Giữa kỳ: 7.8/10"},
    {"code": "ECON1101", "name": "Kinh tế vi mô", "credits": 3, "status": "warning", "note": "2 bài tập nộp trễ hạn"},
    {"code": "STAT1102", "name": "Xác suất thống kê", "credits": 3, "status": "normal", "note": "Giữa kỳ: 7.5/10"},
    {"code": "ENGL2201", "name": "Tiếng Anh chuyên ngành", "credits": 3, "status": "good", "note": "Giữa kỳ: 8.0/10"},
]
# Các cảnh báo nổi bật cho banner (sau này lấy từ bảng alerts, mức cao/trung bình chưa xử lý)
BANNER_ALERTS = [
    {"course": "Cơ sở dữ liệu", "detail": "điểm kiểm tra giữa kỳ 5.5/10"},
    {"course": "Kinh tế vi mô", "detail": "2 bài tập cá nhân nộp trễ hạn"},
]


# ---------------- Hàm tính toán (giữ nguyên khi chuyển sang CSDL) ----------------
def classify(gpa):
    for threshold, label in CLASSIFICATION:
        if gpa >= threshold:
            return label
    return "Dưới trung bình"


# Hệ tọa độ SVG của biểu đồ GPA. Điểm, số và nhãn học kỳ nằm CÙNG một SVG nên luôn thẳng hàng.
CHART_W, CHART_H = 640, 300
CHART_LEFT, CHART_RIGHT = 56, 616   # vùng vẽ theo chiều ngang
CHART_TOP, CHART_BASE = 44, 240     # đỉnh và đáy vùng vẽ theo chiều dọc
CHART_INSET = 48                    # chừa hai đầu để nhãn không sát mép


def build_gpa_chart(terms, target):
    gpas = [g for _, g in terms]
    # Trục dọc thu gọn quanh dữ liệu (bậc 0.2) để thấy rõ xu hướng; nhãn trục ghi rõ giá trị
    lo = math.floor((min(gpas + [target]) - 0.15) * 5) / 5
    hi = math.ceil((max(gpas + [target]) + 0.15) * 5) / 5

    def y_of(g):
        return round(CHART_BASE - (g - lo) / (hi - lo) * (CHART_BASE - CHART_TOP), 1)

    n = len(terms)
    span = CHART_RIGHT - CHART_LEFT - 2 * CHART_INSET
    xs = [round(CHART_LEFT + CHART_INSET + (i * span / (n - 1) if n > 1 else span / 2), 1)
          for i in range(n)]
    points = [{"x": x, "y": y_of(g), "gpa": g, "label": label, "last": i == n - 1}
              for i, (x, (label, g)) in enumerate(zip(xs, terms))]
    ticks = [{"gpa": round(lo + i * 0.2, 1), "y": y_of(lo + i * 0.2)}
             for i in range(round((hi - lo) / 0.2) + 1)]
    steady = all(b >= a for a, b in zip(gpas, gpas[1:]))
    return {
        "w": CHART_W, "h": CHART_H, "left": CHART_LEFT, "right": CHART_RIGHT,
        "top": CHART_TOP, "base": CHART_BASE,
        "points": points,
        "ticks": ticks,
        "target": {"gpa": target, "y": y_of(target)},
        "line": " ".join(f"{p['x']},{p['y']}" for p in points),  # đường gấp khúc dự phòng khi tắt JS
        "trend_label": "Tăng trưởng ổn định" if steady else "Có biến động giữa các học kỳ",
    }


def get_overview():
    cfg = current_app.config
    last_gpa = GPA_BY_TERM[-1][1]
    prev_gpa = GPA_BY_TERM[-2][1] if len(GPA_BY_TERM) > 1 else None
    total = cfg["TOTAL_PROGRAM_CREDITS"]
    done_pct = round(EARNED_CREDITS / total * 100)
    current_credits = sum(c["credits"] for c in CURRENT_COURSES)

    return {
        "student": current_student(),
        "semester": {
            "label": cfg["SEMESTER_LABEL"],
            "week": cfg["SEMESTER_WEEK"],
            "total_weeks": cfg["SEMESTER_TOTAL_WEEKS"],
        },
        "kpi": {
            "cumulative_gpa": CUMULATIVE_GPA,
            "classification": classify(CUMULATIVE_GPA),
            "last_term_gpa": last_gpa,
            "last_term_delta": round(last_gpa - prev_gpa, 2) if prev_gpa is not None else None,
            "earned_credits": EARNED_CREDITS,
            "total_credits": total,
            "done_pct": done_pct,
            "remaining_credits": total - EARNED_CREDITS,
            "course_count": len(CURRENT_COURSES),
            "current_credits": current_credits,
        },
        "alert_banner": {"term": cfg["SEMESTER_LABEL"].replace(" - ", "-"), "entries": BANNER_ALERTS},
        "gpa_target": GPA_TARGET,
        "gpa_chart": build_gpa_chart(GPA_BY_TERM, GPA_TARGET),
        "highlights": {
            "best_course": BEST_COURSE,
            "a_credits": A_GRADE_CREDITS,
            "a_pct": round(A_GRADE_CREDITS / EARNED_CREDITS * 100, 1),
        },
        "courses": CURRENT_COURSES,
    }


# ---------------- DỮ LIỆU MÔ PHỎNG: trang Kết quả học tập ----------------
# Dữ liệu này chỉ phục vụ trình diễn giao diện; chưa phải dữ liệu thật của NEU.
RESULTS_SEMESTERS = [
    {"value": "hk1-26-27", "label": "Học kỳ 1 • 2026 - 2027 (Hiện tại)"},
    {"value": "hk2-25-26", "label": "Học kỳ 2 • 2025 - 2026"},
    {"value": "hk1-25-26", "label": "Học kỳ 1 • 2025 - 2026"},
    {"value": "hk2-24-25", "label": "Học kỳ 2 • 2024 - 2025"},
]

RESULTS_COURSES = [
    {
        "code": "ITEC1120", "name": "Lập trình Web", "short_name": "L.Trình Web",
        "credits": 3, "attendance": 10.0, "midterm": 8.5, "final": 8.0,
        "total": 8.3, "letter": "A-", "points": 3.7,
        "weight": "Chuyên cần 10% • Giữa kỳ 30% • Cuối kỳ 60%",
        "assessment": "Thực hành phòng máy", "note": "Dữ liệu minh họa.",
    },
    {
        "code": "ITEC1125", "name": "Cơ sở dữ liệu", "short_name": "CS Dữ liệu",
        "credits": 3, "attendance": 9.0, "midterm": 5.5, "final": 6.5,
        "total": 6.2, "letter": "C", "points": 2.0,
        "weight": "Chuyên cần 10% • Giữa kỳ 30% • Cuối kỳ 60%",
        "assessment": "Bài tập và bài thi cuối kỳ", "note": "Cần chú ý cải thiện kết quả học tập.",
    },
    {
        "code": "ITEC2105", "name": "Phân tích thiết kế hệ thống", "short_name": "PTTK H.Thống",
        "credits": 3, "attendance": 9.0, "midterm": 8.0, "final": 8.0,
        "total": 8.1, "letter": "A", "points": 3.5,
        "weight": "Chuyên cần 10% • Giữa kỳ 30% • Cuối kỳ 60%",
        "assessment": "Bài tập lớn và bài thi", "note": "Dữ liệu minh họa.",
    },
    {
        "code": "ECON1101", "name": "Kinh tế vi mô", "short_name": "Kinh tế Vi mô",
        "credits": 3, "attendance": 8.0, "midterm": 6.5, "final": 6.5,
        "total": 6.8, "letter": "B-", "points": 2.7,
        "weight": "Chuyên cần 10% • Giữa kỳ 30% • Cuối kỳ 60%",
        "assessment": "Tự luận", "note": "Dữ liệu minh họa.",
    },
    {
        "code": "STAT1102", "name": "Xác suất thống kê", "short_name": "Xác suất TK",
        "credits": 3, "attendance": 9.5, "midterm": 7.5, "final": 7.8,
        "total": 7.9, "letter": "B", "points": 3.0,
        "weight": "Chuyên cần 10% • Giữa kỳ 30% • Cuối kỳ 60%",
        "assessment": "Bài tập và bài thi", "note": "Dữ liệu minh họa.",
    },
    {
        "code": "ENGL2201", "name": "Tiếng Anh chuyên ngành", "short_name": "Anh chuyên ngành",
        "credits": 3, "attendance": 10.0, "midterm": 8.0, "final": 8.5,
        "total": 8.5, "letter": "A", "points": 4.0,
        "weight": "Chuyên cần 10% • Giữa kỳ 30% • Cuối kỳ 60%",
        "assessment": "Thuyết trình và bài thi", "note": "Dữ liệu minh họa.",
    },
]


def get_results():
    """Dữ liệu hiển thị cho trang Kết quả học tập (bản demo, chưa nối CSDL)."""
    courses = [dict(course) for course in RESULTS_COURSES]
    total_credits = sum(course["credits"] for course in courses)
    return {
        "student": current_student(),
        "results_semesters": RESULTS_SEMESTERS,
        "selected_semester": "hk1-26-27",
        "results_courses": courses,
        "results_summary": {
            "semester_label": "HK1 2026 - 2027",
            "gpa": 3.25,
            "average_score": 7.63,
            "registered_credits": total_credits,
            "course_count": len(courses),
            "passed_count": len(courses),
            "not_passed_count": 0,
        },
    }
