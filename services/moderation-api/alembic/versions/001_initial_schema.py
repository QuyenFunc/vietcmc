"""initial schema

Revision ID: 001
Revises: 
Create Date: 2025-10-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clients table
    op.create_table(
        'clients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('app_id', sa.String(length=64), nullable=False),
        sa.Column('organization_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('api_key', sa.String(length=128), nullable=False),
        sa.Column('hmac_secret', sa.String(length=128), nullable=False),
        sa.Column('webhook_url', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_clients_created_at', 'clients', ['created_at'], unique=False)
    op.create_index('idx_clients_status', 'clients', ['status'], unique=False)
    op.create_index(op.f('ix_clients_api_key'), 'clients', ['api_key'], unique=True)
    op.create_index(op.f('ix_clients_app_id'), 'clients', ['app_id'], unique=True)
    op.create_index(op.f('ix_clients_email'), 'clients', ['email'], unique=True)
    op.create_index(op.f('ix_clients_id'), 'clients', ['id'], unique=False)

    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(length=64), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.String(length=255), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('job_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.Column('moderation_result', sa.String(length=20), nullable=True),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_duration_ms', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_jobs_client_id', 'jobs', ['client_id'], unique=False)
    op.create_index('idx_jobs_client_status_created', 'jobs', ['client_id', 'status', 'created_at'], unique=False)
    op.create_index('idx_jobs_created_at', 'jobs', ['created_at'], unique=False)
    op.create_index('idx_jobs_moderation_result', 'jobs', ['moderation_result'], unique=False)
    op.create_index('idx_jobs_status', 'jobs', ['status'], unique=False)
    op.create_index(op.f('ix_jobs_client_id'), 'jobs', ['client_id'], unique=False)
    op.create_index(op.f('ix_jobs_id'), 'jobs', ['id'], unique=False)
    op.create_index(op.f('ix_jobs_job_id'), 'jobs', ['job_id'], unique=True)

    # Create webhook_logs table
    op.create_table(
        'webhook_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(length=64), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('webhook_url', sa.Text(), nullable=False),
        sa.Column('request_payload', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('request_headers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('response_status_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_webhook_logs_client_id', 'webhook_logs', ['client_id'], unique=False)
    op.create_index('idx_webhook_logs_job_id', 'webhook_logs', ['job_id'], unique=False)
    op.create_index('idx_webhook_logs_sent_at', 'webhook_logs', ['sent_at'], unique=False)
    op.create_index('idx_webhook_logs_status', 'webhook_logs', ['status'], unique=False)
    op.create_index(op.f('ix_webhook_logs_client_id'), 'webhook_logs', ['client_id'], unique=False)
    op.create_index(op.f('ix_webhook_logs_id'), 'webhook_logs', ['id'], unique=False)
    op.create_index(op.f('ix_webhook_logs_job_id'), 'webhook_logs', ['job_id'], unique=False)


def downgrade() -> None:
    op.drop_table('webhook_logs')
    op.drop_table('jobs')
    op.drop_table('clients')

