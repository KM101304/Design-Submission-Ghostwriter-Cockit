from fastapi import Header


async def tenant_id(x_tenant_id: str = Header(default="demo-brokerage")) -> str:
    return x_tenant_id
