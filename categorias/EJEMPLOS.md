Ejemplos de uso de la API de categorías

- Listar categorías: GET /api/categorias/
- Crear categoría: POST /api/categorias/ { "nombre": "Ropa", "descripcion": "..." }
- Obtener categoría: GET /api/categorias/<id>/
- Actualizar categoría: PUT/PATCH /api/categorias/<id>/
- Desactivar (soft delete): DELETE /api/categorias/<id>/
- Buscar por nombre: GET /api/categorias/buscar/?nombre=Ropa
