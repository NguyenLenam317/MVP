from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create traffic_snapshots table
    op.create_table('traffic_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('visits', sa.Integer(), nullable=False),
        sa.Column('page_views', sa.Integer(), nullable=False),
        sa.Column('bounce_rate', sa.Float(), nullable=False),
        sa.Column('avg_visit_duration', sa.Float(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('direct_traffic', sa.Integer(), nullable=False),
        sa.Column('organic_traffic', sa.Integer(), nullable=False),
        sa.Column('paid_traffic', sa.Integer(), nullable=False),
        sa.Column('social_traffic', sa.Integer(), nullable=False),
        sa.Column('referral_traffic', sa.Integer(), nullable=False),
        sa.Column('country_distribution', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('device_distribution', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_traffic_snapshots_brand_id'), 'traffic_snapshots', ['brand_id'], unique=False)
    op.create_index(op.f('ix_traffic_snapshots_date'), 'traffic_snapshots', ['date'], unique=False)

    # Create seo_info table
    op.create_table('seo_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('keywords', sa.Integer(), nullable=False),
        sa.Column('organic_traffic', sa.Integer(), nullable=False),
        sa.Column('paid_traffic', sa.Integer(), nullable=False),
        sa.Column('organic_keywords', sa.Integer(), nullable=False),
        sa.Column('paid_keywords', sa.Integer(), nullable=False),
        sa.Column('seo_score', sa.Float(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_seo_info_brand_id'), 'seo_info', ['brand_id'], unique=False)
    op.create_index(op.f('ix_seo_info_date'), 'seo_info', ['date'], unique=False)

    # Create sentiment_results table
    op.create_table('sentiment_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('review_id', sa.Integer(), nullable=True),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('label', sa.String(length=20), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['social_posts.id'], ),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sentiment_results_post_id'), 'sentiment_results', ['post_id'], unique=False)
    op.create_index(op.f('ix_sentiment_results_review_id'), 'sentiment_results', ['review_id'], unique=False)

    # Update brands table
    op.add_column('brands', sa.Column('social_handles', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.create_index(op.f('ix_brands_social_handles'), 'brands', ['social_handles'], unique=False)

def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_brands_social_handles'), table_name='brands')
    op.drop_index(op.f('ix_sentiment_results_review_id'), table_name='sentiment_results')
    op.drop_index(op.f('ix_sentiment_results_post_id'), table_name='sentiment_results')
    op.drop_index(op.f('ix_seo_info_date'), table_name='seo_info')
    op.drop_index(op.f('ix_seo_info_brand_id'), table_name='seo_info')
    op.drop_index(op.f('ix_traffic_snapshots_date'), table_name='traffic_snapshots')
    op.drop_index(op.f('ix_traffic_snapshots_brand_id'), table_name='traffic_snapshots')

    # Drop tables
    op.drop_column('brands', 'social_handles')
    op.drop_table('sentiment_results')
    op.drop_table('seo_info')
    op.drop_table('traffic_snapshots')
