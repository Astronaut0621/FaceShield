from app.models.file_record import FileRecord


def serialize_file_record(record: FileRecord) -> dict:
    return {
        "file_id": record.id,
        "original_filename": record.original_filename,
        "stored_filename": record.stored_filename,
        "file_url": record.file_url,
        "file_size": record.file_size,
        "file_type": record.file_type,
    }

