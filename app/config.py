import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    # Tham số minh họa: sau này đọc từ CSDL / bảng học kỳ
    SEMESTER_LABEL = "HK1 2026 - 2027"
    SEMESTER_WEEK = 9
    SEMESTER_TOTAL_WEEKS = 16
    TOTAL_PROGRAM_CREDITS = 130
