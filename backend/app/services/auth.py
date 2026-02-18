from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Tenant, User


ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    salted = f"{settings.auth_password_salt}:{password}".encode("utf-8")
    return hashlib.sha256(salted).hexdigest()


def verify_password(password: str, expected_hash: str) -> bool:
    provided = hash_password(password)
    return hmac.compare_digest(provided, expected_hash)


def create_access_token(*, sub: str, tenant_external_id: str) -> tuple[str, int]:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.auth_access_token_exp_minutes)
    payload = {
        "sub": sub,
        "tenant_external_id": tenant_external_id,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    token = jwt.encode(payload, settings.auth_secret_key, algorithm=ALGORITHM)
    return token, settings.auth_access_token_exp_minutes * 60


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.auth_secret_key, algorithms=[ALGORITHM])


def ensure_seed_user(db: Session) -> User:
    tenant = db.scalar(select(Tenant).where(Tenant.external_id == settings.auth_seed_tenant_id))
    if not tenant:
        tenant = Tenant(external_id=settings.auth_seed_tenant_id, name=settings.auth_seed_tenant_id)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    user = db.scalar(select(User).where(User.email == settings.auth_seed_email))
    if user:
        return user

    user = User(
        tenant_id=tenant.id,
        email=settings.auth_seed_email,
        password_hash=hash_password(settings.auth_seed_password),
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
