#!/usr/bin/env python3
"""
Script to seed database with test users and products.
Run this before starting the backend.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base
from app.core.security import hash_password
from app.models.producto import Product
from app.models.user import User, UserRole


async def seed_database():
    """Create tables and insert test data."""

    engine = create_async_engine(
        settings.get_database_url(),
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            users = [
                User(
                    nombre="Admin",
                    email="admin@restaurante.com",
                    password_hash=hash_password("admin123"),
                    rol=UserRole.ADMIN,
                    activo=True,
                ),
                User(
                    nombre="Juan Mesero",
                    email="mesero@restaurante.com",
                    password_hash=hash_password("mesero123"),
                    rol=UserRole.MESERO,
                    activo=True,
                ),
                User(
                    nombre="Chef Cocina",
                    email="cocina@restaurante.com",
                    password_hash=hash_password("cocina123"),
                    rol=UserRole.COCINA,
                    activo=True,
                ),
                User(
                    nombre="Caja Principal",
                    email="cajero@restaurante.com",
                    password_hash=hash_password("cajero123"),
                    rol=UserRole.CAJERO,
                    activo=True,
                ),
            ]

            for user in users:
                session.add(user)

            products = [
                Product(
                    nombre="Pizza Personal",
                    descripcion="Pizza con mozzarella y tomate",
                    precio=30.00,
                    categoria="pizzas",
                    disponible=True,
                ),
                Product(
                    nombre="Ensalada Cesar",
                    descripcion="Ensalada fresca con aderezos",
                    precio=18.00,
                    categoria="ensaladas",
                    disponible=True,
                ),
                Product(
                    nombre="Hamburguesa",
                    descripcion="Hamburguesa con queso y carnes premium",
                    precio=25.00,
                    categoria="burgers",
                    disponible=True,
                ),
                Product(
                    nombre="Bebida Gaseosa",
                    descripcion="Refresco frio",
                    precio=5.00,
                    categoria="bebidas",
                    disponible=True,
                ),
            ]

            for product in products:
                session.add(product)

            await session.commit()
            print("Database seeded successfully")
            print("Test users created:")
            print("  - admin@restaurante.com / admin123 (ADMIN)")
            print("  - mesero@restaurante.com / mesero123 (MESERO)")
            print("  - cocina@restaurante.com / cocina123 (COCINA)")
            print("  - cajero@restaurante.com / cajero123 (CAJERO)")
            print("\n4 test products created (Pizza, Ensalada, Hamburguesa, Bebida)")

        except Exception as exc:
            print(f"Error seeding database: {exc}")
            await session.rollback()
            raise

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
