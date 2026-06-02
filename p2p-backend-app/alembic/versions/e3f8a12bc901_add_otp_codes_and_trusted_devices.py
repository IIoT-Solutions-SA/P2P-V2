"""add otp_codes and trusted_devices tables

Revision ID: e3f8a12bc901
Revises: abc123def456
Create Date: 2026-06-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'e3f8a12bc901'
down_revision = 'abc123def456'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create otp_codes table
    op.create_table(
        'otp_codes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('purpose', sa.String(50), nullable=False),
        sa.Column('code_hash', sa.String(64), nullable=False),
        sa.Column('challenge_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_otp_codes_email', 'otp_codes', ['email'])
    op.create_index('ix_otp_codes_challenge_id', 'otp_codes', ['challenge_id'])

    # Create trusted_devices table
    op.create_table(
        'trusted_devices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_email', sa.String(255), nullable=False),
        sa.Column('device_token', sa.String(128), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_trusted_devices_user_email', 'trusted_devices', ['user_email'])
    op.create_index('ix_trusted_devices_device_token', 'trusted_devices', ['device_token'])


def downgrade() -> None:
    op.drop_index('ix_trusted_devices_device_token', table_name='trusted_devices')
    op.drop_index('ix_trusted_devices_user_email', table_name='trusted_devices')
    op.drop_table('trusted_devices')

    op.drop_index('ix_otp_codes_challenge_id', table_name='otp_codes')
    op.drop_index('ix_otp_codes_email', table_name='otp_codes')
    op.drop_table('otp_codes')
