"""
Script to update database schema with new tables.
Run this after adding new models.
"""
from app.db.session import engine, Base
from app.models import User, SwaggerDoc, Endpoint, Agent


def update_database():
    """Create new tables without dropping existing ones."""
    print("Updating database schema...")
    print("Creating new tables (if they don't exist)...")
    
    # This will only create tables that don't exist yet
    # Existing tables won't be modified
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database schema updated successfully!")
    print("\nNew tables added:")
    print("  - users")
    print("  - swagger_docs")
    print("  - endpoints")
    print("  - agents")
    

if __name__ == "__main__":
    update_database()