"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-07-11 19:50:00.000000

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
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('schools',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_schools_name'), 'schools', ['name'], unique=True)
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('role', sa.Enum('STUDENT', 'PROFESSOR', 'ADMIN', name='userrole'), nullable=False),
    sa.Column('auth_provider', sa.String(), nullable=False),
    sa.Column('external_id', sa.String(), nullable=False),
    sa.Column('google_refresh_token', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('external_id')
    )
    op.create_table('courses',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('code', sa.String(length=8), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('school_id', sa.Integer(), nullable=True),
    sa.Column('crn', sa.String(length=10), nullable=True),
    sa.Column('semester', sa.String(length=6), nullable=True),
    sa.Column('professor_calendar_token', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_courses_code'), 'courses', ['code'], unique=True)
    op.create_table('course_events',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('start_ts', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_ts', sa.DateTime(timezone=True), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('location', sa.Text(), nullable=True),
    sa.Column('professor_gcal_event_id', sa.Text(), nullable=True),
    sa.Column('content_hash', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('enrollments',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'course_id', name='_user_course_uc')
    )
    op.create_table('events',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('dt_start', sa.DateTime(timezone=True), nullable=False),
    sa.Column('dt_end', sa.DateTime(timezone=True), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('student_course_links',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('student_calendar_token', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id', 'course_id', name='_student_course_uc')
    )
    op.create_table('syllabi',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('filename', sa.String(), nullable=False),
    sa.Column('file_url', sa.String(), nullable=True),
    sa.Column('file_size', sa.String(), nullable=True),
    sa.Column('parsed_text', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='syllabusstatus'), server_default='pending', nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('syllabi')
    op.drop_table('student_course_links')
    op.drop_table('events')
    op.drop_table('enrollments')
    op.drop_table('course_events')
    op.drop_table('courses')
    op.drop_table('users')
    op.drop_table('schools')
    # ### end Alembic commands ###