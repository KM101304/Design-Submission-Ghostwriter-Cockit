from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Tenant, User
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import create_access_token, ensure_seed_user, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    ensure_seed_user(db)

    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    tenant = db.get(Tenant, user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Tenant missing")

    token, expires_in = create_access_token(sub=str(user.id), tenant_external_id=tenant.external_id)
    return TokenResponse(access_token=token, tenant_id=tenant.external_id, expires_in=expires_in)
