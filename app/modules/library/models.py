
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "library.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                credits INTEGER NOT NULL,
                instructor TEXT,
                progress INTEGER DEFAULT 0,
                category TEXT
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM courses"
        ).fetchone()[0]

        if count == 0:
            sample_courses = [
                ("ITEC 320", "Lập trình Web & Ứng dụng Doanh nghiệp", 3,
                 "TS. Lê Hoàng Nam", 85, "Công nghệ thông tin"),
                ("ITEC 204", "Cơ sở dữ liệu nâng cao & Tối ưu truy vấn", 3,
                 "PGS.TS. Vũ Thị Thu Hương", 90, "Công nghệ thông tin"),
                ("KTL 301", "Kinh tế lượng ứng dụng & Phân tích chuỗi thời gian", 3,
                 "TS. Trần Đức Huy", 62, "Kinh tế & Phân tích"),
                ("KTKT 102", "Kinh tế vi mô 2", 3,
                 "PGS.TS. Hoàng Minh Tâm", 78, "Kinh tế & Phân tích"),
                ("TCNH 210", "Quản trị Tài chính Doanh nghiệp", 3,
                 "TS. Lê Minh Tuấn", 80, "Tài chính")
            ]

            conn.executemany("""
                INSERT INTO courses
                (course_code, name, credits, instructor, progress, category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, sample_courses)

        conn.commit()

    finally:
        conn.close()


def get_course(course_code):
    conn = get_db()

    try:
        row = conn.execute(
            "SELECT * FROM courses WHERE course_code = ?",
            (course_code,)
        ).fetchone()

        return dict(row) if row else None

    finally:
        conn.close()


def get_courses(category=None):
    conn = get_db()

    try:
        if category:
            rows = conn.execute(
                "SELECT * FROM courses WHERE category = ?",
                (category,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM courses"
            ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()
