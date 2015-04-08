"""
intial_v1.2

Revision ID: 30b4cd1b3ebf
Revises: 
Create Date: 2015-04-08 12:47:43.129062
This is the script which I created from an empty database up to the first release like build.
"""

# revision identifiers, used by Alembic.
from pylons.configuration import config
from joj.websetup import setup_app

revision = '30b4cd1b3ebf'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    """
    Upgrade the database from nothing
    :return: nothing
    """

    op.create_table('account_request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('institution', sa.String(length=255), nullable=True),
    sa.Column('usage', sa.String(length=1000), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('driving_datasets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('geographic_region', sa.String(length=255), nullable=True),
    sa.Column('spatial_resolution', sa.String(length=255), nullable=True),
    sa.Column('temporal_resolution', sa.String(length=255), nullable=True),
    sa.Column('boundary_lat_north', sa.Float(), nullable=True),
    sa.Column('boundary_lat_south', sa.Float(), nullable=True),
    sa.Column('boundary_lon_east', sa.Float(), nullable=True),
    sa.Column('boundary_lon_west', sa.Float(), nullable=True),
    sa.Column('time_start', sa.DateTime(), nullable=True),
    sa.Column('time_end', sa.DateTime(), nullable=True),
    sa.Column('view_order_index', sa.Integer(), nullable=True),
    sa.Column('usage_order_index', sa.Integer(), nullable=True),
    sa.Column('is_restricted_to_admins', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('code_versions',
    sa.Column('id', sa.SmallInteger(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('is_default', sa.Boolean(), nullable=True),
    sa.Column('url_base', sa.String(length=1000), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dataset_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=30), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('model_run_statuses',
    sa.Column('id', sa.SmallInteger(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('system_alerts_emails',
    sa.Column('id', sa.SmallInteger(), nullable=False),
    sa.Column('code', sa.String(length=255), nullable=True),
    sa.Column('last_sent', sa.DateTime(), nullable=True),
    sa.Column('sent_frequency_in_s', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('land_cover_values',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=1000), nullable=True),
    sa.Column('index', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('output_variables',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('depends_on_nsmax', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_levels',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('namelist_files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=1000), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('access_level', sa.String(length=255), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('institution', sa.String(length=255), nullable=True),
    sa.Column('storage_quota_in_gb', sa.BigInteger(), nullable=True),
    sa.Column('model_run_creation_action', sa.String(length=255), nullable=True),
    sa.Column('forgotten_password_uuid', sa.String(length=255), nullable=True),
    sa.Column('forgotten_password_expiry_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('land_cover_region_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=1000), nullable=True),
    sa.Column('driving_dataset_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['driving_dataset_id'], ['driving_datasets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('driving_dataset_locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('base_url', sa.String(length=1000), nullable=True),
    sa.Column('var_name', sa.String(length=255), nullable=True),
    sa.Column('driving_dataset_id', sa.Integer(), nullable=True),
    sa.Column('dataset_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dataset_type_id'], ['dataset_types.id'], ),
    sa.ForeignKeyConstraint(['driving_dataset_id'], ['driving_datasets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('model_runs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('error_message', sa.String(length=1000), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_submitted', sa.DateTime(), nullable=True),
    sa.Column('date_started', sa.DateTime(), nullable=True),
    sa.Column('last_status_change', sa.DateTime(), nullable=True),
    sa.Column('time_elapsed_secs', sa.BigInteger(), nullable=True),
    sa.Column('status_id', sa.SmallInteger(), nullable=True),
    sa.Column('code_version_id', sa.SmallInteger(), nullable=True),
    sa.Column('science_configuration_id', sa.Integer(), nullable=True),
    sa.Column('driving_dataset_id', sa.Integer(), nullable=True),
    sa.Column('driving_data_lat', sa.Float(), nullable=True),
    sa.Column('driving_data_lon', sa.Float(), nullable=True),
    sa.Column('driving_data_rows', sa.Integer(), nullable=True),
    sa.Column('land_cover_frac', sa.String(length=255), nullable=True),
    sa.Column('science_configuration_spinup_in_years', sa.Integer(), nullable=True),
    sa.Column('storage_in_mb', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['code_version_id'], ['code_versions.id'], ),
    sa.ForeignKeyConstraint(['driving_dataset_id'], ['driving_datasets.id'], ),
    sa.ForeignKeyConstraint(['science_configuration_id'], ['model_runs.id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['model_run_statuses.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('namelists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('namelist_file_id', sa.Integer(), nullable=True),
    sa.Column('index_in_file', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['namelist_file_id'], ['namelist_files.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('datasets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('wms_url', sa.String(length=255), nullable=True),
    sa.Column('netcdf_url', sa.String(length=255), nullable=True),
    sa.Column('low_res_url', sa.String(length=255), nullable=True),
    sa.Column('dataset_type_id', sa.Integer(), nullable=True),
    sa.Column('viewable_by_user_id', sa.Integer(), nullable=True),
    sa.Column('data_range_from', sa.Float(), nullable=True),
    sa.Column('data_range_to', sa.Float(), nullable=True),
    sa.Column('is_categorical', sa.Boolean(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.Column('is_input', sa.Boolean(), nullable=True),
    sa.Column('model_run_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dataset_type_id'], ['dataset_types.id'], ),
    sa.ForeignKeyConstraint(['model_run_id'], ['model_runs.id'], ),
    sa.ForeignKeyConstraint(['viewable_by_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('parameters',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('default_value', sa.String(length=1000), nullable=True),
    sa.Column('type', sa.String(length=255), nullable=True),
    sa.Column('required', sa.Boolean(), nullable=True),
    sa.Column('min', sa.Integer(), nullable=True),
    sa.Column('min_inclusive', sa.Boolean(), nullable=True),
    sa.Column('max', sa.Integer(), nullable=True),
    sa.Column('max_inclusive', sa.Boolean(), nullable=True),
    sa.Column('url_suffix', sa.String(length=1000), nullable=True),
    sa.Column('user_level_id', sa.Integer(), nullable=True),
    sa.Column('namelist_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['namelist_id'], ['namelists.id'], ),
    sa.ForeignKeyConstraint(['user_level_id'], ['user_levels.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('land_cover_regions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=1000), nullable=True),
    sa.Column('mask_file', sa.String(length=4000), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['land_cover_region_categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('model_files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('path', sa.String(length=4000), nullable=True),
    sa.Column('is_input', sa.Boolean(), nullable=True),
    sa.Column('model_run_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['model_run_id'], ['model_runs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('driving_dataset_parameter_values',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parameter_id', sa.Integer(), nullable=True),
    sa.Column('value', sa.String(length=1000), nullable=True),
    sa.Column('driving_dataset_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['driving_dataset_id'], ['driving_datasets.id'], ),
    sa.ForeignKeyConstraint(['parameter_id'], ['parameters.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('land_cover_actions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value_id', sa.Integer(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('region_id', sa.Integer(), nullable=True),
    sa.Column('model_run_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['model_run_id'], ['model_runs.id'], ),
    sa.ForeignKeyConstraint(['region_id'], ['land_cover_regions.id'], ),
    sa.ForeignKeyConstraint(['value_id'], ['land_cover_values.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('parameter_code_version_association',
    sa.Column('parameter', sa.Integer(), nullable=True),
    sa.Column('code_version', sa.SmallInteger(), nullable=True),
    sa.ForeignKeyConstraint(['code_version'], ['code_versions.id'], ),
    sa.ForeignKeyConstraint(['parameter'], ['parameters.id'], )
    )
    op.create_table('parameter_values',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=1000), nullable=True),
    sa.Column('model_run_id', sa.Integer(), nullable=True),
    sa.Column('parameter_id', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['model_run_id'], ['model_runs.id'], ),
    sa.ForeignKeyConstraint(['parameter_id'], ['parameters.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    """
    Downgrade the database
    :return: nothing
    """

    op.drop_table('parameter_values')
    op.drop_table('parameter_code_version_association')
    op.drop_table('land_cover_actions')
    op.drop_table('driving_dataset_parameter_values')
    op.drop_table('model_files')
    op.drop_table('land_cover_regions')
    op.drop_table('parameters')
    op.drop_table('datasets')
    op.drop_table('namelists')
    op.drop_table('model_runs')
    op.drop_table('driving_dataset_locations')
    op.drop_table('land_cover_region_categories')
    op.drop_table('users')
    op.drop_table('namelist_files')
    op.drop_table('user_levels')
    op.drop_table('output_variables')
    op.drop_table('land_cover_values')
    op.drop_table('system_alerts_emails')
    op.drop_table('model_run_statuses')
    op.drop_table('dataset_types')
    op.drop_table('code_versions')
    op.drop_table('driving_datasets')
    op.drop_table('account_request')