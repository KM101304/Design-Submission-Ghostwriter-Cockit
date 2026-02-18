from fastapi import Depends, Header, HTTPException, status

from app.api.deps.auth import current_user
from app.models.entities import User


async def tenant_id(
    user: User = Depends(current_user),
    x_tenant_id: str | None = Header(default=None),
) -> str:
    tenant_external_id = user.tenant.external_id if hasattr(user, "tenant") and user.tenant else None
    if x_tenant_id and tenant_external_id and x_tenant_id != tenant_external_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    return x_tenant_id or tenant_external_id or "demo-brokerage"
