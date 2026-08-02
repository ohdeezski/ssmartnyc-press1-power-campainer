import os
import uuid

from werkzeug.utils import secure_filename

from app.config import Config
from app.extensions import db
from app.modules.storage.models import StoredFile


class FileManager:
    def __init__(self):
        self.base_dir = Config.UPLOAD_FOLDER

    def _allowed_extensions(self, category, cfg):
        """Return the allowed extension set for a category, or None = unrestricted."""

        def get(name):
            return cfg.get(name, getattr(Config, name, set()))

        if category in ("audio", "voice"):
            return get("ALLOWED_AUDIO_EXTENSIONS")
        if category in ("numbers", "contacts"):
            return get("ALLOWED_NUMBER_EXTENSIONS")
        if category == "templates":
            return get("ALLOWED_TEMPLATE_EXTENSIONS")
        if category in ("images", "brand"):
            return get("ALLOWED_IMAGE_EXTENSIONS")
        if category == "assets":
            return (
                get("ALLOWED_AUDIO_EXTENSIONS")
                | get("ALLOWED_IMAGE_EXTENSIONS")
                | get("ALLOWED_DOCUMENT_EXTENSIONS")
            )
        return None

    def upload(self, file_obj, category, subcategory, user_id=None):
        if not file_obj.filename:
            return None, "No file selected"

        from flask import current_app, has_app_context

        cfg = current_app.config if has_app_context() else Config

        filename = secure_filename(file_obj.filename)
        ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

        # Enforce the per-category extension whitelist before writing anything.
        allowed = self._allowed_extensions(category, cfg)
        if allowed is not None and ext not in allowed:
            return None, f"File type '.{ext}' is not allowed for category '{category}'"

        unique_name = f"{uuid.uuid4().hex}_{filename}"
        target_dir = os.path.join(self.base_dir, category, subcategory)
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, unique_name)

        file_obj.save(target_path)
        file_size = os.path.getsize(target_path)

        if file_size > Config.MAX_FILE_SIZE:
            os.remove(target_path)
            return None, f"File exceeds maximum size of {Config.MAX_FILE_SIZE} bytes"

        stored = StoredFile(
            original_name=filename,
            stored_name=unique_name,
            category=category,
            subcategory=subcategory,
            file_path=target_path,
            file_size=file_size,
            file_extension=ext,
            created_by=user_id,
        )
        db.session.add(stored)
        db.session.commit()
        return stored, None

    def list_files(self, category=None, subcategory=None, page=1, per_page=50):
        query = StoredFile.query
        if category:
            query = query.filter_by(category=category)
        if subcategory:
            query = query.filter_by(subcategory=subcategory)
        return query.order_by(StoredFile.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def delete_file(self, file_id):
        stored = StoredFile.query.get(file_id)
        if stored:
            if os.path.exists(stored.file_path):
                os.remove(stored.file_path)
            db.session.delete(stored)
            db.session.commit()
            return True
        return False

    def get_file(self, file_id):
        return StoredFile.query.get(file_id)

    def search(self, query, category=None):
        from sqlalchemy import or_

        search = f"%{query}%"
        q = StoredFile.query.filter(
            or_(
                StoredFile.original_name.ilike(search),
                StoredFile.stored_name.ilike(search),
            )
        )
        if category:
            q = q.filter_by(category=category)
        return q.order_by(StoredFile.created_at.desc()).all()


file_manager = FileManager()
