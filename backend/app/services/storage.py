from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import boto3
from botocore.client import BaseClient

from app.core.config import settings


class StorageClient:
    def put_bytes(self, key: str, content: bytes, content_type: str) -> str:
        raise NotImplementedError

    def public_url(self, key: str) -> str:
        raise NotImplementedError


class LocalStorageClient(StorageClient):
    def __init__(self, root: str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put_bytes(self, key: str, content: bytes, content_type: str) -> str:
        destination = self.root / key
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        return key

    def public_url(self, key: str) -> str:
        if settings.storage_public_base_url:
            return f"{settings.storage_public_base_url.rstrip('/')}/{quote(key)}"
        return f"file://{(self.root / key).resolve()}"


class S3StorageClient(StorageClient):
    def __init__(self, client: BaseClient, bucket: str) -> None:
        self.client = client
        self.bucket = bucket

    def put_bytes(self, key: str, content: bytes, content_type: str) -> str:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content, ContentType=content_type)
        return key

    def public_url(self, key: str) -> str:
        if settings.storage_public_base_url:
            return f"{settings.storage_public_base_url.rstrip('/')}/{quote(key)}"
        endpoint = settings.storage_s3_endpoint or ""
        if endpoint:
            return f"{endpoint.rstrip('/')}/{self.bucket}/{quote(key)}"
        region = settings.storage_s3_region
        return f"https://{self.bucket}.s3.{region}.amazonaws.com/{quote(key)}"


def safe_filename(filename: str) -> str:
    allowed = "._-"
    cleaned = "".join(ch if ch.isalnum() or ch in allowed else "_" for ch in filename)
    return cleaned or "upload.bin"


_storage: StorageClient | None = None


def get_storage() -> StorageClient:
    global _storage
    if _storage is not None:
        return _storage

    if settings.storage_backend == "s3":
        session = boto3.session.Session()
        client = session.client(
            "s3",
            endpoint_url=settings.storage_s3_endpoint or None,
            aws_access_key_id=settings.storage_s3_access_key or None,
            aws_secret_access_key=settings.storage_s3_secret_key or None,
            region_name=settings.storage_s3_region,
        )
        _storage = S3StorageClient(client=client, bucket=settings.storage_bucket)
    else:
        _storage = LocalStorageClient(root=settings.storage_local_path)
    return _storage
