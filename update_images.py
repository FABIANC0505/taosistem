import urllib.request, urllib.parse, json

# Login
data = json.dumps({"email": "admin@restaurante.com", "password": "admin123"}).encode()
token = json.loads(urllib.request.urlopen(
    urllib.request.Request("http://localhost:8000/auth/login", data=data, headers={"Content-Type": "application/json"})
).read())["access_token"]
print("✅ Logged in")

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

# Get products
products = json.loads(urllib.request.urlopen(
    urllib.request.Request("http://localhost:8000/products", headers=headers)
).read())

# Map name fragments to image paths (frontend static)
IMAGE_MAP = {
    "pizza":    "/img/pizza_personal.png",
    "ensalada": "/img/ensalada_cesar.png",
    "hamburguesa": "/img/hamburguesa.png",
    "bebida":   "/img/bebida_gaseosa.png",
}

updated = 0
for p in products:
    nombre_lower = p["nombre"].lower()
    for keyword, img_path in IMAGE_MAP.items():
        if keyword in nombre_lower:
            patch = json.dumps({"imagen_url": img_path}).encode()
            req = urllib.request.Request(
                f"http://localhost:8000/products/{p['id']}",
                data=patch,
                headers=headers,
                method="PUT"
            )
            try:
                resp = urllib.request.urlopen(req)
                print(f"  → Updated '{p['nombre']}' with {img_path}")
                updated += 1
            except Exception as e:
                print(f"  ✗ Error updating {p['nombre']}: {e}")
            break

print(f"\n✅ Updated {updated}/{len(products)} products with images")
