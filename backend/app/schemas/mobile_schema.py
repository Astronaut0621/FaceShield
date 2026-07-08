from pydantic import BaseModel


class MobileEndpointInfo(BaseModel):
    login: str
    detect: str
    records: str
    model_version: str


class MobileUploadPolicy(BaseModel):
    max_upload_size: int
    allowed_extensions: list[str]


class MobileAlgorithmInfo(BaseModel):
    backend: str
    ready: bool
    model_name: str | None = None
    model_version: str | None = None
    warnings: list[str] = []


class MobileBootstrapResponse(BaseModel):
    status: str
    api_version: str
    server_time: str
    endpoints: MobileEndpointInfo
    upload_policy: MobileUploadPolicy
    algorithm: MobileAlgorithmInfo
