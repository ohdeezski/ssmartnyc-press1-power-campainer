from alembic import context
from sqlalchemy import engine_from_config, pool
import os
import sys

# Add the project root to sys.path so app can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Import the Flask app and db to get the actual metadata
from app import create_app, db

app = create_app("development")

# Set the target_metadata from the Flask-SQLAlchemy db
target_metadata = db.metadata

# Override sqlalchemy.url so Alembic targets the same instance/ DB
# that Flask-SQLAlchemy uses (sqlite:///campaigns.db is relative to
# the instance folder, but Alembic resolves it relative to CWD).
db_url = "sqlite:///" + os.path.join(app.instance_path, "campaigns.db")
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
