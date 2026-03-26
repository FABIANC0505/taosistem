#!/usr/bin/env python3
"""
Create a visual product catalog with local SVG images and insert/update products.
"""

import asyncio
from pathlib import Path

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.producto import Product


UPLOADS_DIR = Path("uploads/products")


SVG_ASSETS = {
    "catalog-burger.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect width="800" height="600" fill="#f8efe2"/>
  <ellipse cx="400" cy="510" rx="240" ry="34" fill="#d9c4a6"/>
  <path d="M200 250c10-90 85-150 200-150s190 60 200 150H200z" fill="#d9903d"/>
  <circle cx="280" cy="185" r="8" fill="#fff3d0"/><circle cx="360" cy="145" r="7" fill="#fff3d0"/>
  <circle cx="430" cy="165" r="6" fill="#fff3d0"/><circle cx="520" cy="190" r="7" fill="#fff3d0"/>
  <rect x="190" y="255" width="420" height="26" rx="12" fill="#6f3f1d"/>
  <rect x="170" y="280" width="460" height="24" rx="12" fill="#3c8d32"/>
  <rect x="185" y="303" width="430" height="58" rx="20" fill="#6b2b20"/>
  <rect x="210" y="360" width="380" height="24" rx="12" fill="#f1c14d"/>
  <rect x="195" y="387" width="410" height="70" rx="18" fill="#d48d3d"/>
</svg>
""",
    "catalog-pizza.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect width="800" height="600" fill="#fbf1de"/>
  <circle cx="400" cy="300" r="210" fill="#e8b356"/>
  <circle cx="400" cy="300" r="182" fill="#f4dc8f"/>
  <circle cx="280" cy="240" r="26" fill="#b43d2a"/><circle cx="450" cy="200" r="24" fill="#b43d2a"/>
  <circle cx="520" cy="310" r="28" fill="#b43d2a"/><circle cx="330" cy="370" r="24" fill="#b43d2a"/>
  <circle cx="450" cy="400" r="22" fill="#b43d2a"/>
  <path d="M295 170l35 25-20 34-33-18zM515 245l34 22-22 34-30-19zM350 430l33 21-21 31-31-17z" fill="#2f8b57"/>
  <path d="M235 430c58-49 126-74 165-85 1 70-14 135-30 178-53-14-96-41-135-93z" fill="#edc467"/>
  <path d="M235 430c58-49 126-74 165-85-1 44-8 91-18 132-54-1-104-18-147-47z" fill="#f4dc8f"/>
</svg>
""",
    "catalog-pasta.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect width="800" height="600" fill="#f6eee8"/>
  <ellipse cx="400" cy="335" rx="220" ry="145" fill="#ffffff"/>
  <ellipse cx="400" cy="350" rx="250" ry="160" fill="none" stroke="#d6d6d6" stroke-width="18"/>
  <path d="M265 320c28-70 89-110 142-110 62 0 116 34 145 102-27 38-82 67-147 67-63 0-115-23-140-59z" fill="#f2cf6c"/>
  <path d="M292 304c26-41 63-71 109-71 55 0 95 22 125 67-26 30-69 52-123 52-47 0-89-18-111-48z" fill="#ed9a47"/>
  <path d="M317 265c12 35 26 55 41 55s28-18 39-55c15 39 33 58 50 58 16 0 30-18 39-52" fill="none" stroke="#f7e19a" stroke-width="12" stroke-linecap="round"/>
  <circle cx="350" cy="270" r="10" fill="#49793d"/><circle cx="437" cy="260" r="9" fill="#49793d"/><circle cx="485" cy="318" r="10" fill="#49793d"/>
</svg>
""",
    "catalog-steak.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect width="800" height="600" fill="#efe6e0"/>
  <ellipse cx="400" cy="510" rx="220" ry="35" fill="#d0c4bd"/>
  <path d="M205 320c0-102 91-180 201-180 77 0 142 32 177 83 40 8 72 42 72 87 0 72-72 145-173 167-129 29-277-41-277-157z" fill="#6f231d"/>
  <path d="M260 320c0-61 58-110 130-110 54 0 102 24 124 61 34 6 57 31 57 62 0 47-44 94-110 108-91 20-201-28-201-121z" fill="#9a342d"/>
  <path d="M318 317c0-35 31-63 70-63 29 0 54 15 65 36 19 5 31 19 31 36 0 29-28 57-69 64-48 8-97-24-97-73z" fill="#f4dccb"/>
  <circle cx="602" cy="237" r="35" fill="#f2efe8"/><circle cx="602" cy="237" r="20" fill="#ddd8d1"/>
</svg>
""",
    "catalog-soda.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect width="800" height="600" fill="#edf5fb"/>
  <path d="M370 90h60l8 55h-76z" fill="#4fb4ff"/>
  <path d="M340 145h120l-22 330a34 34 0 0 1-34 30h-8a34 34 0 0 1-34-30z" fill="#2793e8"/>
  <path d="M330 145h140v26H330z" fill="#156db5"/>
  <path d="M390 70h18v40h-18z" fill="#f4f9ff"/>
  <path d="M368 232c28-18 78-17 104 1M360 286c37-21 96-20 126 4M357 346c35-24 99-23 131 4" fill="none" stroke="#8fd1ff" stroke-width="10" stroke-linecap="round"/>
  <circle cx="300" cy="170" r="10" fill="#9ed7ff"/><circle cx="520" cy="220" r="14" fill="#9ed7ff"/><circle cx="270" cy="285" r="8" fill="#9ed7ff"/>
</svg>
""",
    "catalog-beer.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect width="800" height="600" fill="#fff3d7"/>
  <path d="M285 180h220v250c0 45-36 80-80 80h-60c-44 0-80-35-80-80z" fill="#e0a128"/>
  <path d="M310 225h170v180c0 35-28 64-64 64h-42c-36 0-64-29-64-64z" fill="#f0bc36"/>
  <path d="M505 230h35c29 0 55 24 55 55s-26 55-55 55h-35v-35h25c11 0 20-9 20-20s-9-20-20-20h-25z" fill="none" stroke="#d6d7db" stroke-width="24"/>
  <circle cx="320" cy="170" r="34" fill="#ffffff"/><circle cx="360" cy="145" r="40" fill="#ffffff"/><circle cx="410" cy="154" r="45" fill="#ffffff"/><circle cx="458" cy="170" r="34" fill="#ffffff"/>
  <rect x="305" y="165" width="170" height="36" rx="18" fill="#ffffff"/>
</svg>
""",
    "catalog-juice.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect width="800" height="600" fill="#fff1e3"/>
  <path d="M290 140h220l-24 310c-3 39-35 70-74 70h-24c-39 0-71-31-74-70z" fill="#ff8f2b"/>
  <path d="M320 175h160l-18 240c-2 28-24 50-52 50h-20c-28 0-50-22-52-50z" fill="#ffb03b"/>
  <path d="M448 110h12l40 70h-12z" fill="#5aa85d"/>
  <path d="M452 110c42-34 85-28 105-4-25 2-52 13-74 36z" fill="#76c66f"/>
  <circle cx="250" cy="190" r="12" fill="#ffd39e"/><circle cx="560" cy="245" r="10" fill="#ffd39e"/><circle cx="235" cy="310" r="8" fill="#ffd39e"/>
</svg>
""",
}


CATALOG = [
    ("Hamburguesa Clasica", 22.0, "Pan brioche, carne de res, queso cheddar y vegetales frescos.", "burgers", "/uploads/products/catalog-burger.svg"),
    ("Hamburguesa Doble BBQ", 29.0, "Doble carne, tocineta crocante, salsa BBQ y aros de cebolla.", "burgers", "/uploads/products/catalog-burger.svg"),
    ("Pizza Margarita", 28.0, "Salsa pomodoro, mozzarella fresca y albahaca.", "pizzas", "/uploads/products/catalog-pizza.svg"),
    ("Pizza Pepperoni", 32.0, "Mozzarella extra, pepperoni y orégano tostado.", "pizzas", "/uploads/products/catalog-pizza.svg"),
    ("Pasta Alfredo con Pollo", 31.0, "Pasta cremosa con pollo salteado y queso parmesano.", "pastas", "/uploads/products/catalog-pasta.svg"),
    ("Pasta Bolognesa", 30.0, "Salsa de carne lenta, tomate italiano y albahaca.", "pastas", "/uploads/products/catalog-pasta.svg"),
    ("Carne Asada Tradicional", 39.0, "Corte de res a la parrilla con papa rústica y chimichurri.", "carnes", "/uploads/products/catalog-steak.svg"),
    ("Churrasco Especial", 45.0, "Carne asada con mantequilla de ajo y vegetales grillados.", "carnes", "/uploads/products/catalog-steak.svg"),
    ("Gaseosa Cola", 6.0, "Bebida fría en presentación personal.", "bebidas", "/uploads/products/catalog-soda.svg"),
    ("Gaseosa Limon", 6.0, "Refresco de limón servido bien frío.", "bebidas", "/uploads/products/catalog-soda.svg"),
    ("Cerveza Lager", 9.0, "Cerveza rubia suave y refrescante.", "cervezas", "/uploads/products/catalog-beer.svg"),
    ("Cerveza Artesanal IPA", 12.0, "IPA de perfil cítrico y amargor equilibrado.", "cervezas", "/uploads/products/catalog-beer.svg"),
    ("Jugo Natural de Mango", 8.0, "Jugo natural preparado al momento con fruta fresca.", "jugos", "/uploads/products/catalog-juice.svg"),
    ("Jugo Natural de Fresa", 8.0, "Bebida natural con fresa madura y hielo.", "jugos", "/uploads/products/catalog-juice.svg"),
]


def ensure_assets():
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    for filename, content in SVG_ASSETS.items():
        (UPLOADS_DIR / filename).write_text(content.strip() + "\n", encoding="utf-8")


async def seed_catalog():
    ensure_assets()
    async with AsyncSessionLocal() as db:
        for nombre, precio, descripcion, categoria, imagen_url in CATALOG:
            result = await db.execute(select(Product).where(Product.nombre == nombre))
            product = result.scalar_one_or_none()
            if product:
                product.precio = precio
                product.descripcion = descripcion
                product.categoria = categoria
                product.imagen_url = imagen_url
                product.disponible = True
                print(f"Actualizado: {nombre}")
            else:
                db.add(
                    Product(
                        nombre=nombre,
                        precio=precio,
                        descripcion=descripcion,
                        categoria=categoria,
                        imagen_url=imagen_url,
                        disponible=True,
                    )
                )
                print(f"Creado: {nombre}")
        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed_catalog())
