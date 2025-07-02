"""Initial DB schema.

Revision ID: 0001_initial
Revises: 
Create Date: 2025-07-01
"""
from alembic import op  # type: ignore
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "emails",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("thread_id", sa.String()),
        sa.Column("sender", sa.String()),
        sa.Column("subject", sa.String()),
        sa.Column("snippet", sa.String()),
        sa.Column("category", sa.String(), default="General"),
        sa.Column("job_company", sa.String(), nullable=True),
        sa.Column("job_status", sa.String(), default="Applied"),
        sa.Column("received_at", sa.DateTime()),
    )

    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String()),
        sa.Column("mime_type", sa.String()),
        sa.Column("size", sa.Integer()),
        sa.Column("email_id", sa.String(), sa.ForeignKey("emails.id")),
    )


def downgrade() -> None:
    op.drop_table("attachments")
    op.drop_table("emails")
