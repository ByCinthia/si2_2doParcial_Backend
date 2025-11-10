Endpoints principales (BASE = http://localhost:8000/api/productos)

1) Listar productos (muestra imagen, precios, tallas, stock, descripción)
GET / 
Headers: none (o Authorization si lo deseas)

Respuesta (200):
[
  {
    "id": 1,
    "name": "Zapatilla X",
    "description": "Zapatilla deportiva, cómoda.",
    "price": "120.00",
    "base_price": "120.00",
    "images": [
      {"id":1,"image_url":"https://.../img1.jpg"}
    ],
    "variants": [
      {"id":1,"sku":"ZX-37-BL","size":"37","color":"Negro","model_name":"ZX","price":"120.00","stock":5},
      {"id":2,"sku":"ZX-38-BL","size":"38","color":"Negro","model_name":"ZX","price":"120.00","stock":2}
    ],
    "active": true
  },
  ...
]

2) Detalle de producto
GET /<id>/
Respuesta (200): igual al item anterior + created_at, updated_at.

3) Inventario (variantes con tallas/colores y stock)
GET /<id>/inventory/
Respuesta (200):
[
  {"id":1,"sku":"ZX-37-BL","size":"37","color":"Negro","model_name":"ZX","price":"120.00","stock":5},
  ...
]

4) Actualizar stock de una variante (requiere auth)
PATCH /variants/<variant_id>/stock/
Headers:
  Authorization: Bearer <ACCESS_TOKEN>
Body (JSON):
{"stock": 10}

Respuesta (200):
{"id":1,"sku":"ZX-37-BL","size":"37","color":"Negro","model_name":"ZX","price":"120.00","stock":10}

Notas:
- Las tallas/colores/model_name se guardan en ProductVariant; frontend puede filtrar o agrupar por size/color/model.
- Las imágenes se guardan como URL por simplicidad; si usas storage (cloudinary/local) cambia ProductImage.image_url por ImageField y configura storage.