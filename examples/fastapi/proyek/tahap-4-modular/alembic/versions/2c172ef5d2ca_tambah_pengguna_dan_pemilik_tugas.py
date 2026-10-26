"""tambah pengguna dan pemilik tugas

Revision ID: 2c172ef5d2ca
Revises: 8a4eeca129c7
Create Date: 2026-10-26 20:17:54.189835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '2c172ef5d2ca'
down_revision: Union[str, Sequence[str], None] = '8a4eeca129c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('pengguna',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nama_pengguna', sqlmodel.sql.sqltypes.AutoString(length=30), nullable=False),
    sa.Column('hash_kata_sandi', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('peran', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pengguna_nama_pengguna'), 'pengguna', ['nama_pengguna'], unique=True)
    # Perbaikan manual: SQLite tidak bisa menambah constraint lewat ALTER,
    # jadi dipakai batch_alter_table (tabel disalin ulang oleh Alembic).
    # Constraint juga diberi nama.
    with op.batch_alter_table('tugas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pemilik_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_tugas_pemilik_id_pengguna', 'pengguna', ['pemilik_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('tugas', schema=None) as batch_op:
        batch_op.drop_constraint('fk_tugas_pemilik_id_pengguna', type_='foreignkey')
        batch_op.drop_column('pemilik_id')
    op.drop_index(op.f('ix_pengguna_nama_pengguna'), table_name='pengguna')
    op.drop_table('pengguna')
