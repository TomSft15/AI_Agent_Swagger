from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.db.session import engine, Base
from app.models import User, SwaggerDoc, Endpoint, Agent
from app.core.config import settings

def init_db():
    """Initialize database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def create_first_superuser(db: Session):
    """Create the first superuser if it doesn't exist."""
    # Check if any user exists
    user = db.query(User).first()
    if not user:
        print("Creating first superuser...")
        superuser = User(
            email="admin@example.com",
            username="admin",
            full_name="Admin User",
            hashed_password=get_password_hash(settings.SUPERADMIN_PWD),
            is_active=True,
            is_superuser=True
        )
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        print(f"Superuser created: {superuser.email}")
        print(f"Password: {settings.SUPERADMIN_PWD}")
        print("⚠️  Please change the password immediately!")
    else:
        print("Database already has users. Skipping superuser creation.")


if __name__ == "__main__":
    from app.db.session import SessionLocal
    
    # Initialize database
    init_db()
    
    # Create first superuser
    db = SessionLocal()
    try:
        create_first_superuser(db)
    finally:
        db.close()