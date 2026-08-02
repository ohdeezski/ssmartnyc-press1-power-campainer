from flask import jsonify, request
from flask_login import current_user, login_required

from app.modules.filemanager import filemanager_bp
from app.modules.filemanager.services import file_manager


@filemanager_bp.route("/", methods=["POST"])
@login_required
def upload_file():
    category = request.form.get("category", "general")
    subcategory = request.form.get("subcategory", "default")
    file_obj = request.files.get("file")
    if not file_obj:
        return jsonify({"error": "No file provided"}), 400

    stored, error = file_manager.upload(
        file_obj, category, subcategory, current_user.id
    )
    if error:
        return jsonify({"error": error}), 400
    return jsonify(stored.to_dict()), 201


@filemanager_bp.route("/", methods=["GET"])
@login_required
def list_files():
    category = request.args.get("category")
    subcategory = request.args.get("subcategory")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    pagination = file_manager.list_files(category, subcategory, page, per_page)
    return jsonify(
        {
            "files": [f.to_dict() for f in pagination.items],
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
        }
    )


@filemanager_bp.route("/<int:file_id>", methods=["GET"])
@login_required
def get_file(file_id):
    stored = file_manager.get_file(file_id)
    if not stored:
        return jsonify({"error": "File not found"}), 404
    return jsonify(stored.to_dict())


@filemanager_bp.route("/<int:file_id>", methods=["DELETE"])
@login_required
def delete_file(file_id):
    stored = file_manager.get_file(file_id)
    if not stored:
        return jsonify({"error": "File not found"}), 404
    # Only the uploader (or a user with manage_assets) may delete a file.
    if stored.created_by != current_user.id and not current_user.has_permission(
        "manage_assets"
    ):
        return jsonify({"error": "Unauthorized"}), 403
    success = file_manager.delete_file(file_id)
    if not success:
        return jsonify({"error": "File not found"}), 404
    return jsonify({"status": "deleted"})


@filemanager_bp.route("/search", methods=["GET"])
@login_required
def search_files():
    query = request.args.get("q", "")
    category = request.args.get("category")
    results = file_manager.search(query, category)
    return jsonify([f.to_dict() for f in results])
