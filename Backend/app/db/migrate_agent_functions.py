"""
Migration script to create agent_functions table.
This allows users to add custom descriptions to API functions to help the LLM understand them better.
"""
from sqlalchemy import text
from app.db.session import engine


def migrate_agent_functions_table():
    """Create agent_functions table for storing custom function descriptions."""
    print("🔄 Creating agent_functions table...")

    with engine.connect() as conn:
        try:
            # Create agent_functions table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS agent_functions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id INTEGER NOT NULL,
                    operation_id VARCHAR(255) NOT NULL,
                    method VARCHAR(10) NOT NULL,
                    path VARCHAR(500) NOT NULL,
                    custom_description TEXT,
                    is_enabled INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
                )
            """))
            print("  ✅ Created agent_functions table")

            # Create indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_agent_functions_agent_id
                ON agent_functions(agent_id)
            """))
            print("  ✅ Created index on agent_id")

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_agent_functions_operation_id
                ON agent_functions(operation_id)
            """))
            print("  ✅ Created index on operation_id")

            conn.commit()

        except Exception as e:
            print(f"  ⚠️  Error during migration: {e}")
            conn.rollback()
            raise

    print("\n✅ Migration complete!")
    print("\nUsers can now add custom descriptions to agent functions to help the LLM understand them better.")


if __name__ == "__main__":
    migrate_agent_functions_table()
