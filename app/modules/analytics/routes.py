from flask import jsonify, render_template

from . import api_bp, bp, services


# ---------- Trang giao diện ----------

@bp.route("/tong-quan")
def overview():
    return render_template(
        "analytics/overview.html",
        **services.get_overview()
    )


def _coming_soon(title):
    return render_template(
        "analytics/coming_soon.html",
        page_title=title
    )


@bp.route("/ket-qua")
def results():
    return render_template(
        "analytics/results.html",
        **services.get_results()
    )


@bp.route("/tien-do")
def progress():
    return render_template("analytics/progress.html")


@bp.route("/hoat-dong")
def activity():
    return render_template("analytics/activity.html")


@bp.route("/canh-bao")
def alerts():
    return render_template("analytics/alerts.html")


@bp.route("/muc-tieu")
def goal():
    return render_template("analytics/goals.html")

# ---------- API (cùng một service với trang giao diện) ----------

@api_bp.route("/overview")
def api_overview():
    return jsonify(services.get_overview())