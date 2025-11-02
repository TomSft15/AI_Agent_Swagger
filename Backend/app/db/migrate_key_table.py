"""
Migration script to add LLM API key columns to users table.
Run this to add the new columns without dropping existing data.
"""
from sqlalchemy import text
from app.db.session import engine


def migrate_users_table():
    """Add LLM API key columns to users table."""
    print("🔄 Migrating users table...")
    
    with engine.connect() as conn:
        try:
            # Add openai_api_key column
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN openai_api_key VARCHAR"
            ))
            print("  ✅ Added openai_api_key column")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("  ℹ️  openai_api_key column already exists")
            else:
                print(f"  ⚠️  Error adding openai_api_key: {e}")
        
        try:
            # Add anthropic_api_key column
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN anthropic_api_key VARCHAR"
            ))
            print("  ✅ Added anthropic_api_key column")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("  ℹ️  anthropic_api_key column already exists")
            else:
                print(f"  ⚠️  Error adding anthropic_api_key: {e}")
        
        conn.commit()
    
    print("\n✅ Migration complete!")
    print("\nUsers can now add their personal LLM API keys via:")
    print("  PUT /api/v1/users/me/llm-keys")


if __name__ == "__main__":
    migrate_users_table()