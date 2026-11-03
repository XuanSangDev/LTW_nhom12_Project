from flask import jsonify, render_template

from . import api_bp, bp, services


# ---------- Trang giao diện ----------
@bp.route("/tong-quan")
def overview():
    return render_template("analytics/overview.html", **services.get_overview())


def _coming_soon(title):
    return render_template("analytics/coming_soon.html", page_title=title)


@bp.route("/ket-qua")
def results():
    return render_template("analytics/results.html", **services.get_results())


@bp.route("/tien-do")
def progress():
    return _coming_soon("Tiến độ chương trình")


@bp.route("/hoat-dong")
def activity():
    return _coming_soon("Hoạt động học tập")


@bp.route("/canh-bao")
def alerts():
    return _coming_soon("Cảnh báo sớm")


@bp.route("/muc-tieu")
def goal():
    return _coming_soon("Mục tiêu & mô phỏng GPA")


# ---------- API (cùng một service với trang giao diện) ----------
@api_bp.route("/overview")
def api_overview():
    return jsonify(services.get_overview())
