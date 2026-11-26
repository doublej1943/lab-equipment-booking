import os

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from labbooking.config import migration_database
from labbooking.extensions import db, validate_database


url = migration_database(os.environ)
if context.is_offline_mode():
    context.configure(dialect_name="postgresql", target_metadata=db.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(url, poolclass=NullPool, isolation_level="READ COMMITTED",
                           hide_parameters=True)
    validate_database(engine, application_role=False)
    try:
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=db.metadata)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()
