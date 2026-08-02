from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from logging import getLogger

config = context.config
logger = getLogger("alembic.env")

dialect = config.get_main_option("dialect")
sqlalchemy_url = config.get_main_option("sqlalchemy.url")

def run_migrations_offline():
    url = sqlalchemy_url
    context.configure(
        url=url,
        target_metadata=None,
        literal_binds=True,
        dialect_name=dialect,
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    def run_migrations_online():
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=None)

            try:
                with context.begin_transaction():
                    context.run_migrations()
            except Exception as e:
                logger.error(f"Migration failed: {e}")
                raise

    run_migrations_online()
