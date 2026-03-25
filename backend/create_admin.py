import asyncio
from app.db.session import AsyncSessionLocal, init_db
from app.db.models import User
from app.core.security import get_password_hash


async def create_admin():
    await init_db()

    async with AsyncSessionLocal() as session:
        # Check if admin exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()

        if admin:
            print("Admin user already exists")
            return

        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role="super_admin",
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print("Admin user created successfully")
        print("Username: admin")
        print("Password: admin123")


if __name__ == "__main__":
    asyncio.run(create_admin())