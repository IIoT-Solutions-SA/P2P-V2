"""add distributed failed-login protection state

Revision ID: f4a9c2d78110
Revises: e3f8a12bc901
Create Date: 2026-08-11

"""
from alembic import op
import sqlalchemy as sa


revision = "f4a9c2d78110"
down_revision = "e3f8a12bc901"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # DatabaseManager currently calls Base.metadata.create_all() at application
    # startup. During a rolling/local reload the model can therefore create this
    # table before Alembic records the revision. Keep the migration safe in both
    # deployment orders while Alembic remains the authoritative schema history.
    inspector = sa.inspect(op.get_bind())
    if "login_attempts" not in inspector.get_table_names():
        op.create_table(
            "login_attempts",
            sa.Column("identity_key", sa.String(length=64), nullable=False),
            sa.Column("failed_attempts", sa.Integer(), server_default="0", nullable=False),
            sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_failed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("identity_key"),
        )
        op.create_index("ix_login_attempts_locked_until", "login_attempts", ["locked_until"])
        return

    index_names = {item["name"] for item in inspector.get_indexes("login_attempts")}
    if "ix_login_attempts_locked_until" not in index_names:
        op.create_index("ix_login_attempts_locked_until", "login_attempts", ["locked_until"])


def downgrade() -> None:
    op.drop_index("ix_login_attempts_locked_until", table_name="login_attempts")
    op.drop_table("login_attempts")
