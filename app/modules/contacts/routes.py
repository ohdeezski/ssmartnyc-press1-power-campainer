from flask import jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.modules.contacts import contacts_bp
from app.modules.contacts.models import Contact, ContactList
from app.modules.contacts.services import ContactImportService


@contacts_bp.route("/lists", methods=["GET"])
@login_required
def list_contact_lists():
    lists = ContactList.query.filter_by(created_by=current_user.id).all()
    return jsonify([cl.to_dict() for cl in lists])


@contacts_bp.route("/lists", methods=["POST"])
@login_required
def create_contact_list():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    cl = ContactImportService.create_list(data["name"], data.get("source_file_id"), current_user.id)
    return jsonify(cl.to_dict()), 201


@contacts_bp.route("/lists/<int:list_id>", methods=["GET"])
@login_required
def get_contact_list(list_id):
    cl = ContactList.query.get_or_404(list_id)
    return jsonify(cl.to_dict())


@contacts_bp.route("/lists/<int:list_id>/contacts", methods=["GET"])
@login_required
def list_contacts(list_id):
    cl = ContactList.query.get_or_404(list_id)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    contacts = Contact.query.filter_by(contact_list_id=list_id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify(
        {
            "contacts": [c.to_dict() for c in contacts.items],
            "total": contacts.total,
            "page": page,
            "per_page": per_page,
        }
    )


@contacts_bp.route("/import", methods=["POST"])
@login_required
def import_contacts():
    if "file" not in request.files:
        return jsonify({"error": "file is required"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "filename is required"}), 400

    contact_list_id = request.form.get("contact_list_id", type=int)
    list_name = request.form.get("list_name", "Imported Contacts")

    # Save the uploaded file
    from app.modules.filemanager.services import FileStorageService

    storage = FileStorageService()
    stored = storage.upload(file, "contacts", "import", current_user.id)

    # Create contact list if not provided
    if not contact_list_id:
        cl = ContactImportService.create_list(list_name, stored.id, current_user.id)
        contact_list_id = cl.id

    # Parse and process
    raw_numbers = ContactImportService.parse_file(stored.file_path, stored.file_extension)
    stats, valid_contacts = ContactImportService.process(raw_numbers, contact_list_id, current_user.id)

    # Update list status
    contact_list = ContactList.query.get(contact_list_id)
    contact_list.status = "parsed"
    cl.counts = stats
    db.session.commit()

    return jsonify(
        {
            "contact_list_id": contact_list_id,
            "stats": stats,
            "contacts": [c.to_dict() for c in valid_contacts[:100]],
        }
    )


@contacts_bp.route("/lists/<int:list_id>/commit", methods=["POST"])
@login_required
def commit_contacts(list_id):
    """Finalize a parsed contact list — mark as committed."""
    cl = ContactList.query.get_or_404(list_id)
    if cl.created_by != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    cl.status = "committed"
    cl.committed_at = db.func.now()
    db.session.commit()
    return jsonify(cl.to_dict())


@contacts_bp.route("/lists/<int:list_id>", methods=["DELETE"])
@login_required
def delete_contact_list(list_id):
    cl = ContactList.query.get_or_404(list_id)
    if cl.created_by != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(cl)
    db.session.commit()
    return jsonify({"status": "deleted"})
