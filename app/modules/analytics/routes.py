from flask import jsonify, render_template, request

from . import api_bp, bp, gpa_simulation, services


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
    return render_template("analytics/goals.html", **gpa_simulation.get_goal_context())

# ---------- API (cùng một service với trang giao diện) ----------

@api_bp.route("/overview")
def api_overview():
    return jsonify(services.get_overview())


@api_bp.route("/gpa-simulation")
def api_gpa_simulation():
    """GET /api/analytics/gpa-simulation?target=3.4&scope=semester|graduation"""
    try:
        result = gpa_simulation.simulate(request.args.get("target", ""), request.args.get("scope", gpa_simulation.DEFAULT_SCOPE))
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    return jsonify(result)


@api_bp.route("/semester-projection", methods=["POST"])
def api_semester_projection():
    """POST JSON {target_gpa: 3.5, courses: [{code, final}, ...]}"""
    payload = request.get_json(silent=True) or {}
    try:
        result = gpa_simulation.simulate_semester_courses(
            payload.get("target_gpa", ""), payload.get("courses", []))
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    return jsonify(result)
