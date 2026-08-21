"""Initial database schema migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-20 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure extensions are enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(320), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(512), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('role', sa.String(20), nullable=False, server_default='user'),
        sa.Column('totp_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deletion_requested_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_is_active', 'users', ['is_active'])

    # refresh_tokens
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(512), nullable=False, unique=True),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True)
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'], unique=True)

    # totp_secrets
    op.create_table(
        'totp_secrets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('secret', sa.Text(), nullable=False),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('algorithm', sa.String(10), nullable=False, server_default='SHA1'),
        sa.Column('digits', sa.SmallInteger(), nullable=False, server_default='6'),
        sa.Column('period', sa.SmallInteger(), nullable=False, server_default='30')
    )

    # scan_results
    op.create_table(
        'scan_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('feature_id', sa.String(10), nullable=False),
        sa.Column('input_type', sa.String(20), nullable=False),
        sa.Column('input_hash', sa.String(512), nullable=True),
        sa.Column('risk_level', sa.String(20), nullable=True),
        sa.Column('risk_score_raw', sa.Numeric(5, 4), nullable=True),
        sa.Column('verdict_source', sa.String(20), nullable=True),
        sa.Column('is_experimental', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('task_status', sa.String(20), nullable=True, server_default='queued'),
        sa.Column('scanned_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_code', sa.String(50), nullable=True)
    )
    op.create_index('ix_scan_results_user_id', 'scan_results', ['user_id'])
    op.create_index('ix_scan_results_feature_id', 'scan_results', ['feature_id'])
    op.create_index('ix_scan_results_task_id', 'scan_results', ['task_id'])

    # audit_log
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('event_detail', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_audit_log_event_type', 'audit_log', ['event_type'])
    op.create_index('ix_audit_log_occurred_at', 'audit_log', ['occurred_at'])


def downgrade() -> None:
    op.drop_table('audit_log')
    op.drop_table('scan_results')
    op.drop_table('totp_secrets')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
