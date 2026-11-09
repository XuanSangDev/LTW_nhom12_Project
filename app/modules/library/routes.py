from flask import render_template, jsonify, request, abort

from . import bp
from .models import get_courses, get_course

@bp.route("/khoa-hoc-cua-toi")
def index():
    return render_template("library/index.html")
@bp.route("/khoa-hoc/<course_code>")
def course(course_code):
    selected_course = get_course(course_code)

    if selected_course is None:
        abort(404)

    return render_template(
        "library/course.html",
        course=selected_course
    )

@bp.route("/api/courses")
def api_courses():
    category = request.args.get("category")
    courses = get_courses(category)

    return jsonify({
        "status": "success",
        "data": courses
    })


@bp.route("/bai-giang-slide")
def slide():
    return render_template("library/slide.html")


@bp.route("/kho-tai-nguyen")
def lcms():
    return render_template("library/lcms.html")


@bp.route("/hoc-lieu-da-tai")
def bookmark():
    return render_template("library/bookmark.html")