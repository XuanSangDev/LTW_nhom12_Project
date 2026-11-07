"""QUY TẮC TÍNH ĐIỂM DÙNG CHUNG CHO TOÀN WEBSITE (một nơi duy nhất).

Mọi chỗ cần tính điểm tổng kết hoặc quy đổi thang 10 sang thang 4 (mô phỏng GPA,
trang Kết quả học tập...) phải gọi các hàm trong file này, không tự tính riêng.

Quy tắc đã thống nhất:
  - Trọng số CỐ ĐỊNH cho mọi môn: Chuyên cần 10% - Giữa kỳ 40% - Cuối kỳ 50% (không cho tùy chỉnh).
  - Thang 10: điểm trong [0.0, 10.0]. Thang 4: GPA trong [0.0, 4.0].
  - Điểm cuối kỳ cần đạt được làm tròn LÊN 1 chữ số thập phân.
Dùng Decimal để không bị sai số số thực (ví dụ 8.5 không được thành 8.6).
"""
from decimal import Decimal, InvalidOperation

GPA_MAX = 4.0
SCORE_MAX = 10.0

# Trọng số cố định (phần trăm, số nguyên)
WEIGHT_CC, WEIGHT_GK, WEIGHT_CK = 10, 40, 50
assert WEIGHT_CC + WEIGHT_GK + WEIGHT_CK == 100
WEIGHTS = {"cc": WEIGHT_CC, "gk": WEIGHT_GK, "ck": WEIGHT_CK}
WEIGHTS_TEXT = f"Chuyên cần {WEIGHT_CC}% • Giữa kỳ {WEIGHT_GK}% • Cuối kỳ {WEIGHT_CK}%"

# Bảng quy đổi thang 10 sang thang 4: (điểm thang 10 tối thiểu, điểm chữ, điểm thang 4), xếp từ cao xuống thấp.
# THAM SỐ DO NHÓM TỰ ĐẶT, cần đối chiếu quy chế đào tạo của trường trước khi chốt.
GRADE_SCALE = [
    (Decimal("8.5"), "A", Decimal("4.0")),
    (Decimal("8.0"), "B+", Decimal("3.5")),
    (Decimal("7.0"), "B", Decimal("3.0")),
    (Decimal("6.5"), "C+", Decimal("2.5")),
    (Decimal("5.5"), "C", Decimal("2.0")),
    (Decimal("5.0"), "D+", Decimal("1.5")),
    (Decimal("4.0"), "D", Decimal("1.0")),
    (Decimal("0.0"), "F", Decimal("0.0")),
]

_SCORE_MAX_D = Decimal(str(SCORE_MAX))


def check_score(value, name):
    """Chuyển về Decimal và kiểm tra thuộc [0.0, 10.0]. Ném ValueError nếu sai."""
    try:
        d = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"{name} phải là một con số.")
    if not d.is_finite():
        raise ValueError(f"{name} phải là một con số.")
    if d < 0 or d > _SCORE_MAX_D:
        raise ValueError(f"{name} phải nằm trong khoảng 0.0 đến 10.0 (thang 10).")
    return d


def score_to_points(score):
    """Quy đổi điểm thang 10 sang (điểm thang 4, điểm chữ). Điểm thang 4 không bao giờ vượt 4.0."""
    d = check_score(score, "Điểm")
    for minimum, letter, points in GRADE_SCALE:
        if d >= minimum:
            return float(points), letter
    return 0.0, GRADE_SCALE[-1][1]


def final_total(cc, gk, ck):
    """Điểm tổng kết thang 10 = CC x 10% + GK x 40% + CK x 50%."""
    cc, gk, ck = check_score(cc, "Điểm chuyên cần"), check_score(gk, "Điểm giữa kỳ"), check_score(ck, "Điểm cuối kỳ")
    return float((cc * WEIGHT_CC + gk * WEIGHT_GK + ck * WEIGHT_CK) / 100)




def recognized_score(score, attempt_number=1):
    """Điểm thang 10 được công nhận cho GPA; từ lần học thứ hai trở đi tối đa 7.0.

    Việc chọn lần học hoàn thành gần nhất và không tính trùng học phần được xử lý
    ở tầng truy vấn/backend khi kết nối CSDL.
    """
    d = check_score(score, "Điểm")
    try:
        attempt = int(attempt_number)
    except (TypeError, ValueError):
        raise ValueError("Lần học phải là số nguyên dương.")
    if attempt < 1 or str(attempt_number).strip() != str(attempt):
        raise ValueError("Lần học phải là số nguyên dương.")
    return min(d, Decimal("7.0")) if attempt > 1 else d
