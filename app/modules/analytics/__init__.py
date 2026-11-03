from flask import Blueprint

# Trang giao diện: /phan-tich/...    |   API JSON: /api/analytics/...
bp = Blueprint("analytics", __name__, template_folder="templates")
api_bp = Blueprint("analytics_api", __name__)

from . import routes  # noqa: E402,F401  (đăng ký route sau khi tạo blueprint)
