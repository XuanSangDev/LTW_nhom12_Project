from flask import Flask, request, jsonify, render_template
import sqlite3
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# ==============================
# CẤU HÌNH HỆ THỐNG
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "support.db")

STATUSES = [
    "Chờ xử lý",
    "Đang xử lý",
    "Chờ người học bổ sung",
    "Đã giải quyết",
    "Đã đóng"
]

PRIORITIES = ["Bình thường", "Gấp", "Rất khẩn cấp"]


# ==============================
# KẾT NỐI CƠ SỞ DỮ LIỆU
# ==============================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==============================
# KHỞI TẠO CƠ SỞ DỮ LIỆU
# ==============================

def init_db():
    conn = get_db()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            student_name TEXT NOT NULL,
            student_email TEXT,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Chờ xử lý',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (request_id)
                REFERENCES requests(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        );
    """)

    # Tạo dữ liệu FAQ mẫu nếu chưa có
    count = conn.execute(
        "SELECT COUNT(*) FROM faqs"
    ).fetchone()[0]

    if count == 0:
        faqs = [
            (
                "Tài khoản",
                "Quên mật khẩu tài khoản sinh viên phải làm sao?",
                "Bạn hãy sử dụng chức năng quên mật khẩu tại trang đăng nhập."
            ),
            (
                "Học tập",
                "Không xem được bài giảng trên LMS?",
                "Kiểm tra kết nối Internet và thử đăng nhập lại hệ thống."
            ),
            (
                "Học vụ",
                "Làm thế nào để kiểm tra đăng ký tín chỉ?",
                "Truy cập phân hệ đăng ký học phần để kiểm tra trạng thái."
            ),
            (
                "Thi cử",
                "Gặp lỗi khi làm bài thi trực tuyến?",
                "Hãy chụp ảnh lỗi và gửi yêu cầu hỗ trợ đến bộ phận kỹ thuật."
            )
        ]

        conn.executemany("""
            INSERT INTO faqs(category, question, answer)
            VALUES (?, ?, ?)
        """, faqs)

    conn.commit()
    conn.close()


# ==============================
# HÀM HỖ TRỢ
# ==============================

def format_request(row):
    return dict(row)


def get_request_by_code(code):
    conn = get_db()

    item = conn.execute("""
        SELECT * FROM requests
        WHERE code = ?
    """, (code,)).fetchone()

    conn.close()

    return item


# ==============================
# ĐIỀU HƯỚNG CÁC TRANG FRONTEND
# ==============================

# ==============================
# ĐIỀU HƯỚNG CÁC TRANG FRONTEND
# ==============================

@app.route("/")
@app.route("/hotro")
def hotro():
    return render_template("guihotro.html")


@app.route("/guihotro")
def guihotro():
    return render_template("guihotro.html")


@app.route("/myhotro")
def myhotro():
    return render_template("myhotro.html")


@app.route("/chitiet")
def chitiet():
    return render_template("chitiet.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


# ==============================
# API 1: TẠO YÊU CẦU HỖ TRỢ
# ==============================

@app.route("/api/requests", methods=["POST"])
def create_request():

    data = request.get_json(silent=True) or request.form

    student_name = data.get(
        "student_name", "Người học"
    ).strip()

    student_email = data.get(
        "student_email", ""
    ).strip()

    category = data.get(
        "category", ""
    ).strip()

    subject = data.get(
        "subject", ""
    ).strip()

    description = data.get(
        "description", ""
    ).strip()

    priority = data.get(
        "priority", "Bình thường"
    ).strip()

    # Kiểm tra dữ liệu
    if not category:
        return jsonify({
            "success": False,
            "message": "Vui lòng chọn danh mục hỗ trợ."
        }), 400

    if not subject:
        return jsonify({
            "success": False,
            "message": "Vui lòng nhập tiêu đề yêu cầu."
        }), 400

    if not description or len(description) < 10:
        return jsonify({
            "success": False,
            "message": "Mô tả cần có ít nhất 10 ký tự."
        }), 400

    if priority not in PRIORITIES:
        return jsonify({
            "success": False,
            "message": "Mức độ ưu tiên không hợp lệ."
        }), 400

    # Tạo mã yêu cầu
    code = (
        "YC-"
        + datetime.now().strftime("%Y%m%d")
        + "-"
        + uuid.uuid4().hex[:6].upper()
    )

    now = datetime.now().isoformat(timespec="seconds")

    conn = get_db()

    conn.execute("""
        INSERT INTO requests (
            code,
            student_name,
            student_email,
            category,
            subject,
            description,
            priority,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        code,
        student_name,
        student_email,
        category,
        subject,
        description,
        priority,
        "Chờ xử lý",
        now,
        now
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Gửi yêu cầu hỗ trợ thành công!",
        "code": code
    }), 201


# ==============================
# API 2: LẤY DANH SÁCH YÊU CẦU
# ==============================

@app.route("/api/requests", methods=["GET"])
def get_requests():

    keyword = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()

    conn = get_db()

    sql = "SELECT * FROM requests WHERE 1=1"
    params = []

    if keyword:
        sql += """
            AND (
                code LIKE ?
                OR subject LIKE ?
                OR category LIKE ?
            )
        """

        value = f"%{keyword}%"
        params.extend([value, value, value])

    if status:
        sql += " AND status = ?"
        params.append(status)

    sql += " ORDER BY created_at DESC"

    rows = conn.execute(sql, params).fetchall()

    # Thống kê yêu cầu
    statistics = {}

    for item in STATUSES:
        count = conn.execute("""
            SELECT COUNT(*)
            FROM requests
            WHERE status = ?
        """, (item,)).fetchone()[0]

        statistics[item] = count

    conn.close()

    return jsonify({
        "success": True,
        "total": len(rows),
        "statistics": statistics,
        "requests": [format_request(row) for row in rows]
    })


# ==============================
# API 3: XEM CHI TIẾT YÊU CẦU
# ==============================

@app.route("/api/requests/<code>", methods=["GET"])
def request_detail(code):

    conn = get_db()

    item = conn.execute("""
        SELECT * FROM requests
        WHERE code = ?
    """, (code,)).fetchone()

    if item is None:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Không tìm thấy yêu cầu."
        }), 404

    replies = conn.execute("""
        SELECT sender, message, created_at
        FROM replies
        WHERE request_id = ?
        ORDER BY created_at ASC
    """, (item["id"],)).fetchall()

    result = dict(item)
    result["replies"] = [dict(row) for row in replies]

    conn.close()

    return jsonify({
        "success": True,
        "request": result
    })


# ==============================
# API 4: GỬI PHẢN HỒI
# ==============================

@app.route(
    "/api/requests/<code>/replies",
    methods=["POST"]
)
def create_reply(code):

    data = request.get_json(silent=True) or {}

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "success": False,
            "message": "Nội dung phản hồi không được để trống."
        }), 400

    conn = get_db()

    item = conn.execute("""
        SELECT id FROM requests
        WHERE code = ?
    """, (code,)).fetchone()

    if item is None:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Không tìm thấy yêu cầu."
        }), 404

    now = datetime.now().isoformat(timespec="seconds")

    conn.execute("""
        INSERT INTO replies (
            request_id,
            sender,
            message,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        item["id"],
        "Người học",
        message,
        now
    ))

    conn.execute("""
        UPDATE requests
        SET updated_at = ?
        WHERE id = ?
    """, (now, item["id"]))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Gửi phản hồi thành công."
    })


# ==============================
# API 5: CẬP NHẬT TRẠNG THÁI
# ==============================

@app.route(
    "/api/requests/<code>/status",
    methods=["PATCH"]
)
def update_status(code):

    data = request.get_json(silent=True) or {}

    status = data.get("status", "")

    if status not in STATUSES:
        return jsonify({
            "success": False,
            "message": "Trạng thái không hợp lệ."
        }), 400

    conn = get_db()

    item = conn.execute("""
        SELECT id FROM requests
        WHERE code = ?
    """, (code,)).fetchone()

    if item is None:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Không tìm thấy yêu cầu."
        }), 404

    conn.execute("""
        UPDATE requests
        SET status = ?, updated_at = ?
        WHERE code = ?
    """, (
        status,
        datetime.now().isoformat(timespec="seconds"),
        code
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Cập nhật trạng thái thành công."
    })


# ==============================
# API 6: LẤY DANH SÁCH FAQ
# ==============================

@app.route("/api/faqs", methods=["GET"])
def get_faqs():

    keyword = request.args.get("q", "").strip()

    conn = get_db()

    if keyword:
        value = f"%{keyword}%"

        rows = conn.execute("""
            SELECT * FROM faqs
            WHERE question LIKE ?
            OR answer LIKE ?
            OR category LIKE ?
            ORDER BY id DESC
        """, (value, value, value)).fetchall()

    else:
        rows = conn.execute("""
            SELECT * FROM faqs
            ORDER BY id DESC
        """).fetchall()

    conn.close()

    return jsonify({
        "success": True,
        "faqs": [dict(row) for row in rows]
    })


# ==============================
# API 7: THỐNG KÊ TỔNG QUAN
# ==============================

@app.route("/api/statistics", methods=["GET"])
def statistics():

    conn = get_db()

    total = conn.execute("""
        SELECT COUNT(*) FROM requests
    """).fetchone()[0]

    result = {}

    for status in STATUSES:
        result[status] = conn.execute("""
            SELECT COUNT(*)
            FROM requests
            WHERE status = ?
        """, (status,)).fetchone()[0]

    conn.close()

    return jsonify({
        "success": True,
        "total_requests": total,
        "details": result
    })


# ==============================
# XỬ LÝ LỖI
# ==============================

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({
            "success": False,
            "message": "Không tìm thấy dữ liệu."
        }), 404

    return "Không tìm thấy trang.", 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "message": "Lỗi máy chủ. Vui lòng thử lại."
    }), 500


# ==============================
# CHẠY CHƯƠNG TRÌNH
# ==============================

if __name__ == "__main__":

    init_db()

    print("================================")
    print(" NEU LEARNING HUB - BACKEND")
    print(" Máy chủ đang khởi động...")
    print("================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )