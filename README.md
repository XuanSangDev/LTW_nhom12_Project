# NEU Learning Hub: khung dự án Flask (module Phân tích học tập)

## Chạy thử
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run.py                 # mở http://127.0.0.1:5000
python -m unittest discover -s tests -v   # chạy kiểm thử
```
Trang đã hoàn chỉnh: **Tổng quan học tập** (`/phan-tich/tong-quan`).
Các trang còn lại của module 2 đang là trang tạm "đang xây dựng", menu vẫn bấm được.

## Cấu trúc (mỗi module một thư mục, để merge ít xung đột)
```
app/
├── __init__.py            # create_app, đăng ký blueprint, dữ liệu dùng chung cho layout
├── config.py
├── navigation.py          # menu nhóm "Phân tích học tập"
├── shared.py              # sinh viên hiện tại, số cảnh báo chưa đọc (đang giả lập)
├── templates/
│   ├── base.html          # LAYOUT CHUNG: sidebar + thanh trên + chân trang
│   └── partials/          # _sidebar.html, _footer.html, _macros.html (page_header, breadcrumb)
├── static/js/tailwind-config.js   # token màu/chữ/khoảng cách, sửa 1 chỗ dùng cho mọi trang
├── static/img/logo.svg            # logo giữ chỗ, ghi đè bằng logo của nhóm
└── modules/analytics/     # MODULE 2 (của bạn)
    ├── routes.py          # trang giao diện (/phan-tich/...) và API (/api/analytics/...)
    ├── services.py        # dữ liệu mẫu + hàm tính toán (GPA, tiến độ, biểu đồ)
    └── templates/analytics/overview.html
```
Module 1 và 3 tạo thư mục tương tự (`modules/resources`, `modules/support`), rồi đăng ký blueprint trong `app/__init__.py`.

## Thêm một trang mới cho module 2
1. Lấy `code.html` từ Stitch, chỉ copy phần **nội dung chính** (bỏ sidebar, thanh trên, chân trang vì đã có trong `base.html`).
2. Tạo `templates/analytics/<ten>.html`: `{% extends "base.html" %}`, đặt nội dung trong `{% block content %}`, đầu trang dùng macro `page_header`.
3. Viết hàm tính toán trong `services.py`, route trong `routes.py` (route đã có sẵn tên cho 5 trang còn lại).
4. Mục menu tự sáng đúng theo `request.endpoint`, không phải sửa sidebar.

## Lưu ý
- **Dữ liệu là mô phỏng** (viết cứng trong `services.py`), chưa có CSDL. Ngưỡng xếp loại (`CLASSIFICATION`) là tham số nhóm tự đặt, cần đối chiếu quy chế của trường.
- Tailwind đang tải qua CDN (tiện khi phát triển). Khi triển khai thật nên biên dịch ra file CSS.
- Chưa có đăng nhập: `shared.py` đang trả sinh viên giả lập.
- Chưa kiểm tra giao diện trên trình duyệt thật trong môi trường tạo dự án (không tải được CDN), chỉ kiểm tra bằng kiểm thử HTML.
