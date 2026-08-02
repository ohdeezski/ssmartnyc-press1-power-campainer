import os
import uuid

from werkzeug.utils import secure_filename

from app.config import Config
from app.extensions import db
from app.modules.storage.models import StoredFile


class FileStorage:
    def __init__(self, app=None):
        self.app = app
        self.base_dir = Config.UPLOAD_FOLDER

    def init_app(self, app):
        self.app = app
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "numbers", "active"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "numbers", "success"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "numbers", "blacklist"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "audio", "intro"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "audio", "outro"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "audio", "agent"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "audio", "hold"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "audio", "misc"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "templates", "sms"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "templates", "email"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "templates", "whatsapp"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "templates", "telegram"), exist_ok=True)
        os.makedirs(
            os.path.join(self.base_dir, "templates", "messenger"), exist_ok=True
        )
        os.makedirs(
            os.path.join(self.base_dir, "templates", "instagram"), exist_ok=True
        )
        os.makedirs(os.path.join(self.base_dir, "assets", "images"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "assets", "logos"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "assets", "branding"), exist_ok=True)

    def save_file(self, file_obj, category, subcategory, user_id=None):
        filename = secure_filename(file_obj.filename)
        ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        target_dir = os.path.join(self.base_dir, category, subcategory)
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, unique_name)
        file_obj.save(target_path)
        file_size = os.path.getsize(target_path)
        max_size = Config.MAX_FILE_SIZE
        if file_size > max_size:
            os.remove(target_path)
            raise ValueError(f"File exceeds maximum size of {max_size} bytes")
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
        return stored

    def get_file(self, file_id):
        return StoredFile.query.get(file_id)

    def delete_file(self, file_id):
        stored = self.get_file(file_id)
        if stored:
            if os.path.exists(stored.file_path):
                os.remove(stored.file_path)
            db.session.delete(stored)
            db.session.commit()
            return True
        return False

    def list_files(self, category=None, subcategory=None):
        query = StoredFile.query
        if category:
            query = query.filter_by(category=category)
        if subcategory:
            query = query.filter_by(subcategory=subcategory)
        return query.order_by(StoredFile.created_at.desc()).all()

    def validate_file(self, file_obj, allowed_extensions):
        if not file_obj.filename:
            return False, "No file selected"
        ext = (
            file_obj.filename.rsplit(".", 1)[1].lower()
            if "." in file_obj.filename
            else ""
        )
        if ext not in allowed_extensions:
            return (
                False,
                f"File type .{ext} not allowed. Allowed: {', '.join(allowed_extensions)}",
            )
        return True, "Valid"


storage = FileStorage()
