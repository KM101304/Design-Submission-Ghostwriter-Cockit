"""auth users and job tracking

Revision ID: 20260218_0002
Revises: 20260218_0001
Create Date: 2026-02-18 00:15:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260218_0002"
down_revision = "20260218_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("submissions", sa.Column("idempotency_key", sa.String(length=128), nullable=True))
    op.add_column("submissions", sa.Column("job_id", sa.String(length=128), nullable=True))
    op.add_column("submissions", sa.Column("job_status", sa.String(length=64), nullable=False, server_default="processed"))
    op.create_index("ix_submissions_idempotency_key", "submissions", ["idempotency_key"], unique=True)
    op.create_index("ix_submissions_job_id", "submissions", ["job_id"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False, server_default="csr"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_tenant_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_submissions_job_id", table_name="submissions")
    op.drop_index("ix_submissions_idempotency_key", table_name="submissions")
    op.drop_column("submissions", "job_status")
    op.drop_column("submissions", "job_id")
    op.drop_column("submissions", "idempotency_key")
