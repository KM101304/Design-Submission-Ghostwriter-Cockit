"""initial schema

Revision ID: 20260218_0001
Revises: None
Create Date: 2026-02-18 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260218_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tenants_external_id", "tenants", ["external_id"], unique=True)

    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("submission_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("source_object_key", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_submissions_submission_id", "submissions", ["submission_id"], unique=True)
    op.create_index("ix_submissions_tenant_id", "submissions", ["tenant_id"], unique=False)

    op.create_table(
        "profile_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("submission_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("profile_json", sa.Text(), nullable=False),
        sa.Column("completeness_json", sa.Text(), nullable=False),
        sa.Column("questions_json", sa.Text(), nullable=False),
        sa.Column("export_markdown_key", sa.String(length=512), nullable=True),
        sa.Column("export_json_key", sa.String(length=512), nullable=True),
        sa.Column("export_pdf_key", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_profile_versions_submission_id", "profile_versions", ["submission_id"], unique=False)
    op.create_index("ix_profile_versions_tenant_id", "profile_versions", ["tenant_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("submission_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"], unique=False)
    op.create_index("ix_audit_logs_submission_id", "audit_logs", ["submission_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_submission_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_tenant_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_profile_versions_tenant_id", table_name="profile_versions")
    op.drop_index("ix_profile_versions_submission_id", table_name="profile_versions")
    op.drop_table("profile_versions")

    op.drop_index("ix_submissions_tenant_id", table_name="submissions")
    op.drop_index("ix_submissions_submission_id", table_name="submissions")
    op.drop_table("submissions")

    op.drop_index("ix_tenants_external_id", table_name="tenants")
    op.drop_table("tenants")
