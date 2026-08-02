from app.extensions import db
from app.modules.assetlibrary.models import Asset
from app.modules.filemanager.services import file_manager


class AssetLibrary:
    def __init__(self):
        self.file_manager = file_manager

    def add_asset(
        self,
        name,
        asset_type,
        subtype,
        stored_file,
        user_id,
        tags=None,
        extra_data=None,
    ):
        """Create an Asset row referencing an already-uploaded StoredFile.

        Uploading happens exactly once, in the route, via self.file_manager.upload.
        Passing a StoredFile here (not a request file object) prevents the old
        double-upload / AttributeError path.
        """
        asset = Asset(
            name=name,
            type=asset_type,
            subtype=subtype,
            file_id=stored_file.id,
            tags=tags,
            extra_data=extra_data,
            created_by=user_id,
        )
        db.session.add(asset)
        db.session.commit()
        return asset, None

    def list_assets(self, asset_type=None, subtype=None, page=1, per_page=50):
        query = Asset.query
        if asset_type:
            query = query.filter_by(type=asset_type)
        if subtype:
            query = query.filter_by(subtype=subtype)
        return query.order_by(Asset.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    def search(self, query):
        from sqlalchemy import or_

        search = f"%{query}%"
        return (
            Asset.query.filter(or_(Asset.name.ilike(search), Asset.tags.ilike(search)))
            .order_by(Asset.created_at.desc())
            .all()
        )

    def get_asset(self, asset_id):
        return Asset.query.get(asset_id)

    def delete_asset(self, asset_id):
        asset = Asset.query.get(asset_id)
        if asset:
            self.file_manager.delete_file(asset.file_id)
            db.session.delete(asset)
            db.session.commit()
            return True
        return False


asset_library = AssetLibrary()
