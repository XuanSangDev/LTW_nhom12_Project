"""Phần DÙNG CHUNG giữa 3 module (tạm thời giả lập, thay bằng đăng nhập + CSDL thật).

TODO khi làm đăng nhập: current_student() lấy từ phiên đăng nhập (Flask-Login),
unread_alert_count() đếm từ bảng alerts của chính sinh viên đó.
"""


def current_student():
    # Dữ liệu minh họa
    return {
        "id": "11223344",
        "name": "Nguyễn Văn An",
        "initials": "NA",
        "faculty": "Khoa Công nghệ thông tin",
        "class_name": "K64-CNTT02",
        "cohort": 2024,
        "program_type": "Chính quy tập trung",
        "year_label": "Năm 3 • K64 CNTT",
    }


def unread_alert_count():
    # Khớp với "Chưa đọc (2)" ở màn Cảnh báo sớm
    return 2
