import urllib.request
import urllib.parse
import json

try:
    data = json.dumps({"email": "admin@restaurante.com", "password": "admin123"}).encode()
    req1 = urllib.request.Request("http://localhost:8000/auth/login", data=data, headers={"Content-Type": "application/json"})
    resp1 = urllib.request.urlopen(req1)
    token = json.loads(resp1.read())["access_token"]

    payload = {
        "tipo_pedido": "mesa",
        "mesa_numero": 1,
        "items": [{
            "product_id": "1",
            "nombre": "Pizza Personal",
            "cantidad": 1,
            "precio_unitario": 30.0
        }]
    }

    req2 = urllib.request.Request(
        "http://localhost:8000/orders",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    )
    resp2 = urllib.request.urlopen(req2)
    print("SUCCESS", resp2.read().decode())
except urllib.error.HTTPError as e:
    with open('debug_error.json', 'w') as f:
        f.write(e.read().decode())
