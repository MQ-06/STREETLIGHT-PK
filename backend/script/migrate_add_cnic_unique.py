from sqlalchemy import text

from db.database import engine


def migrate():
    """
    Add a unique constraint/index on users.cnic for existing databases.

    New databases created via SQLAlchemy metadata already include the
    uniqueness from the model definition; this migration is only needed
    for databases that were created before unique=True was added.
    """
    with engine.begin() as conn:
        # Postgres-specific: create a unique constraint if it does not already exist
        conn.execute(
            text(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint
                        WHERE conname = 'users_cnic_key'
                    ) THEN
                        ALTER TABLE users
                        ADD CONSTRAINT users_cnic_key UNIQUE (cnic);
                    END IF;
                END;
                $$;
                """
            )
        )


if __name__ == "__main__":
    migrate()
    print("Migration complete: unique constraint on users.cnic ensured.")

