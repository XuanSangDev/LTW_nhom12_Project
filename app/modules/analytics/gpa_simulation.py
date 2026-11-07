"""Logic mô phỏng GPA mục tiêu và GPA học kỳ.

GPA = trung bình cộng điểm quy đổi thang 4 của các học phần được tính GPA;
không nhân trọng số tín chỉ. Tín chỉ chỉ dùng theo dõi tiến độ chương trình.
Dữ liệu số môn trong file services.py hiện là dữ liệu DEMO; backend sẽ thay bằng truy vấn CSDL.
"""
import math
from flask import current_app
from .grading import GPA_MAX, WEIGHTS_TEXT, final_total, score_to_points, check_score
from .services import (
    CUMULATIVE_GPA, CURRENT_COURSES, EARNED_CREDITS, EARNED_GPA_COURSES,
    TOTAL_GPA_COURSES, GPA_TARGET, RESULTS_COURSES,
)

EPS = 1e-9
DEFAULT_SCOPE = "graduation"
SCOPES = {
    "semester": {"label": "GPA tích lũy sau khi kết thúc học kỳ này", "phrase": "sau học kỳ này", "count_text": "môn học kỳ này"},
    "graduation": {"label": "GPA tích lũy khi tốt nghiệp", "phrase": "khi tốt nghiệp", "count_text": "môn còn lại trong chương trình"},
}
STATUS_LABELS = {"impossible": "Không thể đạt", "achieved": "Đã đạt mục tiêu"}


def _floor2(x):
    return math.floor(x * 100 + EPS) / 100


def _ceil2(x):
    return math.ceil(x * 100 - EPS) / 100


def simulate(target, scope=DEFAULT_SCOPE):
    """Tính GPA tích lũy cần đạt; phép tính dựa trên SỐ MÔN, không dựa trên tín chỉ."""
    if scope not in SCOPES:
        raise ValueError("Phạm vi mục tiêu không hợp lệ (chỉ nhận 'semester' hoặc 'graduation').")
    try:
        target = float(target)
    except (TypeError, ValueError):
        raise ValueError("GPA mục tiêu phải là một con số.")
    if not math.isfinite(target) or target < 0 or target > GPA_MAX + EPS:
        raise ValueError("GPA mục tiêu phải nằm trong khoảng 0.00 đến 4.00 (thang 4).")
    target = min(target, GPA_MAX)

    total_credits = int(current_app.config["TOTAL_PROGRAM_CREDITS"])
    earned_credits = int(EARNED_CREDITS)
    current_gpa = float(CUMULATIVE_GPA)
    earned_courses = int(EARNED_GPA_COURSES)
    total_courses = int(TOTAL_GPA_COURSES)
    semester_courses = len(CURRENT_COURSES)
    if total_credits <= 0 or earned_credits < 0 or earned_credits > total_credits:
        raise ValueError("Dữ liệu tín chỉ chương trình không hợp lệ.")
    if total_courses <= 0 or earned_courses < 0 or earned_courses > total_courses:
        raise ValueError("Số môn được tính GPA trong chương trình không hợp lệ.")
    if not math.isfinite(current_gpa) or not 0 <= current_gpa <= GPA_MAX:
        raise ValueError("GPA tích lũy hiện tại không hợp lệ.")

    remaining_courses = total_courses - earned_courses
    in_scope = semester_courses if scope == "semester" else remaining_courses
    if in_scope < 0 or (scope == "semester" and in_scope > remaining_courses):
        raise ValueError("Số môn học kỳ hiện tại không hợp lệ so với chương trình đào tạo.")
    after_courses = earned_courses + in_scope
    meta = SCOPES[scope]

    if in_scope == 0:
        max_reachable = current_gpa
        needed = 0.0 if target <= current_gpa + EPS else float("inf")
    else:
        needed = (target * after_courses - current_gpa * earned_courses) / in_scope
        max_reachable = (current_gpa * earned_courses + GPA_MAX * in_scope) / after_courses

    if needed > GPA_MAX + EPS:
        status, required = "impossible", None
        message = (f"Không thể đạt GPA {target:.2f} {meta['phrase']}: ngay cả khi đạt {GPA_MAX:.2f} "
                   f"ở toàn bộ {in_scope} {meta['count_text']}, GPA tích lũy cao nhất chỉ khoảng "
                   f"{_floor2(max_reachable):.2f}. Hãy chọn mục tiêu không vượt quá {_floor2(max_reachable):.2f}.")
    elif needed <= EPS:
        status, required = "achieved", 0.0
        message = "Bạn đã đạt mức mục tiêu này; không cần GPA tối thiểu bổ sung ở phần môn học còn lại."
    else:
        status, required = "feasible", min(_ceil2(needed), GPA_MAX)
        message = (f"Bạn cần đạt GPA trung bình khoảng {required:.2f}/{GPA_MAX:.2f} "
                   f"trên {in_scope} {meta['count_text']} để GPA tích lũy {meta['phrase']} đạt {target:.2f}.")

    return {
        "target": round(target, 2), "scope": scope, "scope_label": meta["label"],
        "scope_phrase": meta["phrase"], "current_gpa": current_gpa,
        "earned_credits": earned_credits, "total_program_credits": total_credits,
        "remaining_credits": total_credits - earned_credits,
        "earned_gpa_courses": earned_courses, "total_gpa_courses": total_courses,
        "remaining_gpa_courses": remaining_courses, "courses_in_scope": in_scope,
        "courses_after": after_courses,
        "gpa_max": GPA_MAX, "required_gpa": required,
        "max_reachable": round(max_reachable, 4), "max_reachable_floor": _floor2(max_reachable),
        "status": status, "status_label": STATUS_LABELS.get(status), "message": message,
    }


def get_goal_context():
    return {"goal": {
        "target": GPA_TARGET, "scope": DEFAULT_SCOPE, "current_gpa": CUMULATIVE_GPA,
        "slider": {"min": 2.0, "max": GPA_MAX, "step": 0.05},
        "sim": simulate(GPA_TARGET, DEFAULT_SCOPE),
        "courses": [{"code": c["code"], "name": c["name"], "credits": c["credits"],
                     "cc": c["attendance"], "gk": c["midterm"], "final": c["final"]}
                    for c in RESULTS_COURSES],
        "weights_text": WEIGHTS_TEXT,
    }}


def simulate_semester_courses(target_gpa, submitted_courses):
    """Tính GPA học kỳ = trung bình cộng điểm GPA của các môn trong học kỳ."""
    try:
        target = float(target_gpa)
    except (TypeError, ValueError):
        raise ValueError("GPA học kỳ mục tiêu không hợp lệ.")
    if not math.isfinite(target) or target < 0 or target > GPA_MAX:
        raise ValueError("GPA học kỳ mục tiêu phải nằm trong khoảng 0.00 đến 4.00.")
    if not isinstance(submitted_courses, list) or not submitted_courses:
        raise ValueError("Danh sách môn học không hợp lệ.")

    source = {c["code"]: c for c in RESULTS_COURSES}
    submitted = {}
    for item in submitted_courses:
        if not isinstance(item, dict) or item.get("code") not in source:
            raise ValueError("Có môn học không hợp lệ trong danh sách mô phỏng.")
        code = item["code"]
        if code in submitted:
            raise ValueError("Danh sách mô phỏng có mã môn bị trùng.")
        submitted[code] = item

    rows = []
    total_credits = 0
    total_points = 0.0
    for course in RESULTS_COURSES:
        code = course["code"]
        if code not in submitted:
            raise ValueError("Vui lòng nhập điểm cuối kỳ cho tất cả môn học.")
        final_score = check_score(submitted[code].get("final", ""), f"Điểm cuối kỳ môn {course['name']}")
        total = final_total(course["attendance"], course["midterm"], final_score)
        points, letter = score_to_points(total)
        credits = int(course["credits"])
        total_credits += credits
        total_points += points
        rows.append({"code": code, "name": course["name"], "credits": credits,
                     "cc": course["attendance"], "gk": course["midterm"],
                     "final": float(final_score), "total": round(total, 2),
                     "letter": letter, "points": points})

    semester_gpa = total_points / len(rows) if rows else 0.0
    difference = semester_gpa - target
    achieved = difference >= -EPS
    return {
        "target_gpa": round(target, 2), "semester_gpa": round(semester_gpa, 2),
        "difference": round(abs(difference), 2),
        "status": "achieved" if achieved else "below_target",
        "message": (f"Đạt mục tiêu: GPA học kỳ dự kiến {semester_gpa:.2f}, bằng hoặc cao hơn mức cần đạt {target:.2f}."
                    if achieved else f"Chưa đạt mục tiêu: GPA học kỳ dự kiến {semester_gpa:.2f}, còn thiếu {abs(difference):.2f} so với mức cần đạt {target:.2f}."),
        "total_credits": total_credits, "course_count": len(rows), "courses": rows,
    }
