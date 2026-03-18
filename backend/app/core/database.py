from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.get_database_url(), echo=True)
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
    from app.models import User, Product, Order, AppSetting
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE orders ALTER COLUMN mesa_numero DROP NOT NULL"))
        await conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS tipo_pedido VARCHAR(20) NOT NULL DEFAULT 'mesa'"))
        await conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS cliente_nombre VARCHAR(150)"))
        await conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS cliente_telefono VARCHAR(30)"))
        await conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS direccion_entrega TEXT"))
        print("Conexion a PostgreSQL exitosa y tablas creadas")
