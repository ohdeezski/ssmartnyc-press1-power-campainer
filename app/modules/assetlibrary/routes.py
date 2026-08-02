from flask import jsonify, request
from flask_login import current_user, login_required

from app.modules.assetlibrary import assetlibrary_bp
from app.modules.assetlibrary.services import asset_library
from app.modules.filemanager.services import file_manager


@assetlibrary_bp.route("/", methods=["GET"])
@login_required
def list_assets():
    """List all assets for the current user"""
    asset_type = request.args.get("type")
    subtype = request.args.get("subtype")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    assets = asset_library.list_assets(asset_type, subtype, page, per_page)
    return jsonify(
        {
            "assets": [asset.to_dict() for asset in assets.items],
            "page": assets.page,
            "per_page": assets.per_page,
            "total": assets.total,
        }
    )


@assetlibrary_bp.route("/", methods=["POST"])
@login_required
def create_asset():
    """Create a new asset with file upload (multipart form, not JSON)."""
    # Multipart requests carry fields in request.form; request.get_json() is
    # always None here, which previously made every create 400.
    data = request.form

    if "file" not in request.files:
        return jsonify({"error": "File is required"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "File name is required"}), 400

    # Validate required fields
    required_fields = ["name", "type"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    name = data["name"]
    asset_type = data["type"]
    subtype = data.get("subtype")
    tags = data.get("tags")
    extra_data = data.get("extra_data")
    if isinstance(extra_data, str) and extra_data.strip():
        try:
            import json as _json

            extra_data = _json.loads(extra_data)
        except (ValueError, TypeError):
            return jsonify({"error": "extra_data must be valid JSON"}), 400

    # Upload file to file manager exactly once.
    stored_file, error = file_manager.upload(
        file, "assets", subtype or "misc", current_user.id
    )
    if error:
        return jsonify({"error": error}), 400

    # Create asset
    asset, error = asset_library.add_asset(
        name, asset_type, subtype, stored_file, current_user.id, tags, extra_data
    )

    if error:
        # Clean up uploaded file if asset creation fails
        file_manager.delete_file(stored_file.id)
        return jsonify({"error": error}), 400

    return jsonify(asset.to_dict()), 201


@assetlibrary_bp.route("/<int:asset_id>", methods=["GET"])
@login_required
def get_asset(asset_id):
    """Get asset by ID"""
    asset = asset_library.get_asset(asset_id)
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

    # Check if user has permission to access this asset
    if asset.created_by != current_user.id and not current_user.has_permission(
        "view_all"
    ):
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify(asset.to_dict())


@assetlibrary_bp.route("/<int:asset_id>", methods=["PUT"])
@login_required
def update_asset(asset_id):
    """Update asset metadata"""
    asset = asset_library.get_asset(asset_id)
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

    # Check permissions
    if asset.created_by != current_user.id and not current_user.has_permission(
        "edit_campaign"
    ):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Data is required"}), 400

    # Update allowed fields
    if "name" in data:
        asset.name = data["name"]
    if "type" in data:
        asset.type = data["type"]
    if "subtype" in data:
        asset.subtype = data["subtype"]
    if "tags" in data:
        asset.tags = data["tags"]
    if "extra_data" in data:
        asset.extra_data = data["extra_data"]
    if "version" in data:
        asset.version = data["version"]

    asset.save()
    return jsonify(asset.to_dict())


@assetlibrary_bp.route("/<int:asset_id>", methods=["DELETE"])
@login_required
def delete_asset(asset_id):
    """Delete asset and its associated file"""
    asset = asset_library.get_asset(asset_id)
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

    if asset.created_by != current_user.id and not current_user.has_permission(
        "manage_assets"
    ):
        return jsonify({"error": "Unauthorized"}), 403

    success = asset_library.delete_asset(asset_id)
    if success:
        return jsonify({"status": "ok"})
    return jsonify({"error": "Asset not found"}), 404


@assetlibrary_bp.route("/search", methods=["GET"])
@login_required
def search_assets():
    """Search assets by name or tags"""
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    assets = asset_library.search(query)
    return jsonify([asset.to_dict() for asset in assets])


@assetlibrary_bp.route("/<int:asset_id>/file", methods=["GET"])
@login_required
def get_asset_file(asset_id):
    """Get the actual file associated with an asset"""
    asset = asset_library.get_asset(asset_id)
    if not asset or not asset.file_id:
        return jsonify({"error": "Asset or associated file not found"}), 404

    # Check permissions
    if asset.created_by != current_user.id and not current_user.has_permission(
        "view_all"
    ):
        return jsonify({"error": "Unauthorized"}), 403

    stored_file = file_manager.get_file(asset.file_id)
    if not stored_file:
        return jsonify({"error": "Associated file not found"}), 404

    # Return metadata only; never leak the absolute server path.
    return jsonify(
        {
            "file_id": stored_file.id,
            "original_name": stored_file.original_name,
            "stored_name": stored_file.stored_name,
            "file_size": stored_file.file_size,
            "file_extension": stored_file.file_extension,
            "category": stored_file.category,
            "subcategory": stored_file.subcategory,
        }
    )
