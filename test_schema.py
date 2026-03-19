import sys
import os

# Agrega la ruta base de backend
sys.path.insert(0, os.path.abspath('backend'))

from app.schemas.orden import CrearPedidoSchema

import json
try:
    payload = {
        "tipo_pedido": "mesa",
        "mesa_numero": 1,
        "items": [{
            "product_id": "123",
            "nombre": "Test",
            "cantidad": 1,
            "precio_unitario": 10.0
        }]
    }
    json_str = json.dumps(payload)
    obj = CrearPedidoSchema.model_validate_json(json_str)
    print("SUCCESS JSON", obj)
except Exception as e:
    import traceback
    traceback.print_exc()
