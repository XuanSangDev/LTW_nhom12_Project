from flask import Flask, redirect, url_for

from .config import Config
from .navigation import ANALYTICS_ITEMS
from .shared import current_student, unread_alert_count


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Mỗi module = 1 blueprint. Module 1 và 3 đăng ký thêm ở đây khi merge.
    from .modules.analytics import bp as analytics_bp, api_bp as analytics_api_bp

    app.register_blueprint(analytics_bp, url_prefix="/phan-tich")
    app.register_blueprint(analytics_api_bp, url_prefix="/api/analytics")

    @app.route("/")
    def index():
        return redirect(url_for("analytics.overview"))

    @app.context_processor
    def inject_layout_data():
        """Dữ liệu dùng chung cho layout (sidebar, thanh trên) ở mọi trang."""
        return {
            "app_name": "NEU Learning Hub",
            "analytics_items": ANALYTICS_ITEMS,
            "current_student": current_student(),
            "unread_alerts": unread_alert_count(),
        }

    return app
