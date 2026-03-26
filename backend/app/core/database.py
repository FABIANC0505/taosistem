from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.get_database_url(),
    echo=settings.APP_ENV == "development",
)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    from app.models import User, Product, Order, AppSetting, CashSession, CashMovement, CashPayment, WaiterAlert
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Conexion a MySQL exitosa y tablas creadas")
