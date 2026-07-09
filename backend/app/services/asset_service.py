from app.repositories.file_repository import FileRepository
from app.serializers.file_serializer import serialize_file_record


class AssetService:
    def __init__(self, db):
        self.repository = FileRepository(db)

    def list_assets(self, user_id: int, page: int = 1, page_size: int = 20) -> dict:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size
        items = self.repository.list_by_user(user_id=user_id, offset=offset, limit=page_size)
        total = self.repository.count_by_user(user_id=user_id)
        return {
            "total": total,
            "items": [serialize_file_record(item) for item in items],
        }

    def get_asset(self, file_id: int, user_id: int):
        return self.repository.get_active(file_id=file_id, user_id=user_id)

    def delete_asset(self, file_id: int, user_id: int) -> bool:
        return self.repository.soft_delete(file_id=file_id, user_id=user_id)


def list_assets(db, user_id: int, page: int = 1, page_size: int = 20) -> dict:
    return AssetService(db).list_assets(user_id=user_id, page=page, page_size=page_size)
