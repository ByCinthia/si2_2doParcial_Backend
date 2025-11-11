# Ejemplos de uso — app `ventas`

Todos los endpoints asumen base: `http://localhost:8000/api/` y que el usuario está autenticado cuando corresponde (Bearer token o sesión).

## Pedidos (Orders)

Listar pedidos (GET)
````bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/pedidos/

  curl -s -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "items":[
      {"producto_id": 12, "nombre":"Remera Azul", "cantidad":2, "precio":25.50},
      {"producto_id": 15, "nombre":"Pantalón Negro", "cantidad":1, "precio":40.00}
    ],
    "total":91.00,
    "metodo_pago":"tarjeta",
    "datos_cliente":{"nombre":"Ana Perez","direccion":"Calle Falsa 123","telefono":"99999999"},
    "recoger_hasta": null
  }' \
  http://localhost:8000/api/pedidos/
````

Nota sobre imágenes: las imágenes se suben y almacenan desde la app `productos`. Revisa `productos/EJEMPLOS_IMAGENES.md` para cómo subir imágenes y obtener la URL pública que puedes mostrar en recibos/confirmaciones de venta.