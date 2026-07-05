from pydantic import BaseModel


class HistoryItem(BaseModel):
    task_id: int
    file_id: int
    original_filename: str
    label: str | None
    fake_probability: float | None
    risk_level: str | None
    created_at: str | None


class HistoryList(BaseModel):
    total: int
    items: list[HistoryItem]

