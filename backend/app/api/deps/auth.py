from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.entities import Tenant, User
from app.services.auth import decode_access_token


def _extract_bearer(auth_header: str | None) -> str:
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    parts = auth_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    return parts[1]


async def current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if settings.auth_disabled:
        user = db.scalar(select(User).order_by(User.id.asc()))
        if user:
            return user
        tenant = db.scalar(select(Tenant).where(Tenant.external_id == settings.auth_seed_tenant_id))
        if not tenant:
            tenant = Tenant(external_id=settings.auth_seed_tenant_id, name=settings.auth_seed_tenant_id)
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        user = User(
            tenant_id=tenant.id,
            email=settings.auth_seed_email,
            password_hash="disabled-auth",
            role="admin",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    token = _extract_bearer(authorization)
    try:
        payload = decode_access_token(token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.get(User, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user
