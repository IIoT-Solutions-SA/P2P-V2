"""add_user_invitation_table

Revision ID: f89d7b62797d
Revises: ec3cb1e7ea96
Create Date: 2025-08-06 06:37:03.906633

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f89d7b62797d'
down_revision: Union[str, None] = 'ec3cb1e7ea96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_invitations table
    op.create_table(
        'user_invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invited_role', sa.String(length=50), nullable=False),
        sa.Column('invited_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('job_title', sa.String(length=200), nullable=True),
        sa.Column('department', sa.String(length=200), nullable=True),
        sa.Column('personal_message', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('accepted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_user_invitations_email', 'user_invitations', ['email'])
    op.create_index('ix_user_invitations_token', 'user_invitations', ['token'], unique=True)
    op.create_index('ix_user_invitations_organization_id', 'user_invitations', ['organization_id'])
    op.create_index('ix_user_invitations_invited_by', 'user_invitations', ['invited_by'])
    op.create_index('ix_user_invitations_status', 'user_invitations', ['status'])
    op.create_index('ix_user_invitations_expires_at', 'user_invitations', ['expires_at'])
    
    # Add foreign key constraints
    op.create_foreign_key('fk_user_invitations_organization', 'user_invitations', 'organizations', ['organization_id'], ['id'])
    op.create_foreign_key('fk_user_invitations_invited_by', 'user_invitations', 'users', ['invited_by'], ['id'])
    op.create_foreign_key('fk_user_invitations_accepted_by', 'user_invitations', 'users', ['accepted_by'], ['id'])


def downgrade() -> None:
    # Drop foreign key constraints first
    op.drop_constraint('fk_user_invitations_accepted_by', 'user_invitations', type_='foreignkey')
    op.drop_constraint('fk_user_invitations_invited_by', 'user_invitations', type_='foreignkey')
    op.drop_constraint('fk_user_invitations_organization', 'user_invitations', type_='foreignkey')
    
    # Drop indexes
    op.drop_index('ix_user_invitations_expires_at', table_name='user_invitations')
    op.drop_index('ix_user_invitations_status', table_name='user_invitations')
    op.drop_index('ix_user_invitations_invited_by', table_name='user_invitations')
    op.drop_index('ix_user_invitations_organization_id', table_name='user_invitations')
    op.drop_index('ix_user_invitations_token', table_name='user_invitations')
    op.drop_index('ix_user_invitations_email', table_name='user_invitations')
    
    # Drop table
    op.drop_table('user_invitations')
